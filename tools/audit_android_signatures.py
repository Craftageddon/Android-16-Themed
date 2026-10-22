"""Verify distributable APK signatures with installed official Android tools.

Never signs or rewrites upstream artifacts. Certificate pinning is explicit;
development signatures are not silently promoted to release trust.
"""
from pathlib import Path
import argparse,hashlib,json,re,subprocess

def audit(apk,java,jar,expected=None):
 apk=apk.resolve();assert apk.is_file() and apk.suffix.lower()=='.apk'
 p=subprocess.run([str(java),'-jar',str(jar),'verify','--verbose','--print-certs',str(apk)],capture_output=True,text=True,encoding='utf8',errors='replace')
 text=p.stdout+p.stderr
 signer=r'^(?:Signer #\d+|V\d+(?:\.\d+)? Signer:)\s+certificate '
 fingerprints=re.findall(signer+r'SHA-256 digest:\s*([0-9a-fA-F:]+)',text,re.M)
 fingerprints=sorted({f.replace(':','').lower() for f in fingerprints})
 subjects=sorted(set(re.findall(signer+r'DN:\s*(.+)',text,re.M)))
 schemes={key:bool(re.search(r'Verified using '+re.escape(key)+r' scheme[^\n]*:\s*true',text)) for key in ['v1','v2','v3','v3.1','v4']}
 expected=expected.replace(':','').lower() if expected else None
 valid=p.returncode==0 and bool(fingerprints) and (schemes['v2'] or schemes['v3'])
 if expected:assert len(expected)==64 and all(c in '0123456789abcdef' for c in expected),'Expected SHA-256 certificate fingerprint required'
 trust='pinned-match' if expected and set(fingerprints)=={expected} else 'pinned-mismatch' if expected else 'signer-not-pinned'
 return {'file':apk.name,'bytes':apk.stat().st_size,'sha256':hashlib.sha256(apk.read_bytes()).hexdigest(),'cryptographicSignatureValid':valid,'certificateSha256':fingerprints,'certificateSubjects':subjects,'schemes':schemes,'trust':trust,'releaseEligible':valid and trust=='pinned-match' and not any(re.search(r'Android Debug|Local Preview|Development|Android,',s,re.I) for s in subjects),'verificationOutput':text,'deviceInstalled':False}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('apk',type=Path,nargs='+');p.add_argument('--sdk',type=Path,required=True);p.add_argument('--java-home',type=Path,required=True);p.add_argument('--build-tools',default='37.0.0');p.add_argument('--expected-cert-sha256');p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 java=a.java_home/'bin/java.exe';jar=a.sdk/'build-tools'/a.build_tools/'lib/apksigner.jar';assert java.is_file() and jar.is_file()
 rows=[audit(f,java,jar,a.expected_cert_sha256) for f in a.apk];a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps({'date':'2026-10-22','method':'Installed Android apksigner cryptographic verification; no package modification','artifacts':rows,'allSignaturesValid':all(r['cryptographicSignatureValid'] for r in rows),'allReleaseEligible':all(r['releaseEligible'] for r in rows)},indent=2)+'\n')
 print(json.dumps({'audited':len(rows),'allSignaturesValid':all(r['cryptographicSignatureValid'] for r in rows),'releaseEligible':all(r['releaseEligible'] for r in rows)}))
 if not all(r['cryptographicSignatureValid'] for r in rows) or (a.expected_cert_sha256 and not all(r['trust']=='pinned-match' for r in rows)):raise SystemExit(1)
