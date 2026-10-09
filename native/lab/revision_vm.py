from config import *
from native_vm import NativeVM
class RevisionVM(NativeVM):
 def __init__(self,image=IMAGE):
  super().__init__(image=image)
  self.manifest=json.loads((NATIVE/'metadata/ui.json').read_text())
