"""Detached source-artifact signing, distinct from APK/OTA/AVB signing.

Project RSA identity is encrypted at rest; its random encryption password is
protected by Windows DPAPI for the current user. Private material stays ignored.
"""
from pathlib import Path
import argparse,base64,ctypes,hashlib,json,os
from ctypes import wintypes
from cryptography.hazmat.primitives import hashes,serialization
from cryptography.hazmat.primitives.asymmetric import rsa,padding,utils

class Blob(ctypes.Structure):_fields_=[('cbData',wintypes.DWORD),('pbData',ctypes.POINTER(ctypes.c_ubyte))]

def dpapi(data,decrypt=False):
 assert os.name=='nt','DPAPI identity storage requires Windows'
 buffer=ctypes.create_string_buffer(data);source=Blob(len(data),ctypes.cast(buffer,ctypes.POINTER(ctypes.c_ubyte)));target=Blob()
 crypt=ctypes.WinDLL('crypt32',use_last_error=True);kernel=ctypes.WinDLL('kernel32',use_last_error=True)
 if decrypt:
  fn=crypt.CryptUnprotectData;fn.argtypes=[ctypes.POINTER(Blob),ctypes.c_void_p,ctypes.c_void_p,ctypes.c_void_p,ctypes.c_void_p,wintypes.DWORD,ctypes.POINTER(Blob)];args=[ctypes.byref(source),None,None,None,None,1,ctypes.byref(target)]
 else:
  fn=crypt.CryptProtectData;fn.argtypes=[ctypes.POINTER(Blob),wintypes.LPCWSTR,ctypes.c_void_p,ctypes.c_void_p,ctypes.c_void_p,wintypes.DWORD,ctypes.POINTER(Blob)];args=[ctypes.byref(source),'Craftageddon artifact signing',None,None,None,1,ctypes.byref(target)]
 fn.restype=wintypes.BOOL;kernel.LocalFree.argtypes=[ctypes.c_void_p];kernel.LocalFree.restype=ctypes.c_void_p
 if not fn(*args):raise ctypes.WinError(ctypes.get_last_error())
 try:return ctypes.string_at(target.pbData,target.cbData)
 finally:kernel.LocalFree(target.pbData)

def digest(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  while chunk:=f.read(1024*1024):h.update(chunk)
 return h.digest()

def fingerprint(public):return hashlib.sha256(public.public_bytes(serialization.Encoding.DER,serialization.PublicFormat.SubjectPublicKeyInfo)).hexdigest()

def identity(private,public_out):
 private.mkdir(parents=True,exist_ok=True);keyfile=private/'artifact-key.encrypted.pem';secret=private/'artifact-password.dpapi'
 if keyfile.exists() or secret.exists():
  assert keyfile.is_file() and secret.is_file(),'Incomplete identity; do not silently rotate'
  key=serialization.load_pem_private_key(keyfile.read_bytes(),dpapi(secret.read_bytes(),True))
 else:
  key=rsa.generate_private_key(public_exponent=65537,key_size=3072);password=base64.urlsafe_b64encode(os.urandom(48));encrypted=key.private_bytes(serialization.Encoding.PEM,serialization.PrivateFormat.PKCS8,serialization.BestAvailableEncryption(password))
  keyfile.write_bytes(encrypted);secret.write_bytes(dpapi(password))
 public=key.public_key();public_out.parent.mkdir(parents=True,exist_ok=True);public_out.write_bytes(public.public_bytes(serialization.Encoding.PEM,serialization.PublicFormat.SubjectPublicKeyInfo));return key,public

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('mode',choices=['init','sign','verify']);p.add_argument('--private-root',type=Path);p.add_argument('--public-key',type=Path,required=True);p.add_argument('--artifact',type=Path);p.add_argument('--signature',type=Path);p.add_argument('--expected-key-sha256');a=p.parse_args()
 if a.mode in ['init','sign']:
  assert a.private_root is not None;key,public=identity(a.private_root.resolve(),a.public_key.resolve())
 else:public=serialization.load_pem_public_key(a.public_key.read_bytes())
 pin=fingerprint(public)
 if a.expected_key_sha256:assert pin==a.expected_key_sha256.lower(),'Unexpected signing identity'
 if a.mode=='init':print(json.dumps({'publicKeySpkiSha256':pin,'keySize':public.key_size,'privateMaterialPublished':False}))
 else:
  assert a.artifact is not None and a.signature is not None
  data=digest(a.artifact)
  if a.mode=='sign':a.signature.write_bytes(key.sign(data,padding.PSS(mgf=padding.MGF1(hashes.SHA256()),salt_length=32),utils.Prehashed(hashes.SHA256())))
  public.verify(a.signature.read_bytes(),data,padding.PSS(mgf=padding.MGF1(hashes.SHA256()),salt_length=32),utils.Prehashed(hashes.SHA256()))
  result={'artifact':a.artifact.name,'bytes':a.artifact.stat().st_size,'sha256':data.hex(),'signature':a.signature.name,'signatureScheme':'RSA-PSS-3072/SHA-256; MGF1-SHA256; saltLength=32; digest prehashed','publicKeySpkiSha256':pin,'signatureVerified':True,'trustScope':'Craftageddon source-artifact identity; not an APK/OTA/AYN/LineageOS signing certificate'}
  if a.mode=='sign':a.signature.with_suffix(a.signature.suffix+'.json').write_text(json.dumps(result,indent=2)+'\n')
  print(json.dumps(result))
