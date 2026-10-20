"""Create a deterministic complete archive, audit all members and preserve hashes."""
from pathlib import Path
import hashlib,json,sys,zipfile
root=Path(sys.argv[1]).resolve();target=root/'complete-assets.zip'
files=[p for p in sorted(root.rglob('*')) if p.is_file() and p.name not in ['complete-assets.zip','complete-assets.zip.sha256']]
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
 for p in files:
  info=zipfile.ZipInfo(p.relative_to(root).as_posix(),(2026,10,20,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16
  archive.writestr(info,p.read_bytes())
with zipfile.ZipFile(target) as archive:
 assert archive.testzip() is None
 for p in files:assert archive.read(p.relative_to(root).as_posix())==p.read_bytes()
digest=hashlib.sha256(target.read_bytes()).hexdigest();(root/'complete-assets.zip.sha256').write_text(digest+'  complete-assets.zip\n')
print(json.dumps({'archive':target.name,'members':len(files),'bytes':target.stat().st_size,'sha256':digest}))
