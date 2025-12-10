import sys
import types

# Create fake distutils.version module for Python 3.12
class LooseVersion:
    def __init__(self, vstring):
        self.vstring = vstring
    def __str__(self):
        return self.vstring
    def __repr__(self):
        return f"LooseVersion('{self.vstring}')"

# Create module
fake_module = types.ModuleType('distutils.version')
fake_module.LooseVersion = LooseVersion

# Add to sys.modules before buildozer imports it
sys.modules['distutils.version'] = fake_module

print("distutils patched for Python 3.12")
