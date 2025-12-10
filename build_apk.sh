#!/bin/bash
echo "=========================================="
echo "BUILDING EGYPT ARTIFACTS APK"
echo "=========================================="

# Activate venv
source venv/bin/activate

# Apply distutils patch
python -c "
import sys
import types
class LooseVersion:
    def __init__(self, v): self.v = v
    def __str__(self): return self.v
sys.modules['distutils.version'] = types.ModuleType('distutils.version')
sys.modules['distutils.version'].LooseVersion = LooseVersion
print('Python', sys.version)
"

# Accept Android licenses
mkdir -p ~/.android/licenses
echo -e "8933bad161af4178b1185d1a37fbf41ea5269c55\nd56f5187479451eabf01fb78af6dfcb131a6481e\n24333f8a63b6825ea9c5514f83c2829b004d1fee" > ~/.android/licenses/android-sdk-license

# Clean
buildozer android clean

echo "Starting build... (30-60 minutes)"
echo "Be patient - first build downloads everything"
echo "=========================================="

# Build
echo "y" | timeout 7200 buildozer -v android debug 2>&1 | tee build.log

echo "=========================================="
echo "BUILD COMPLETE"
echo "=========================================="

# Check for APK
if compgen -G "bin/*.apk" > /dev/null; then
    APK_FILE=$(ls -t bin/*.apk | head -1)
    echo "✅ SUCCESS! APK created:"
    echo "   File: $(basename "$APK_FILE")"
    echo "   Size: $(du -h "$APK_FILE" | cut -f1)"
    echo ""
    echo "📱 To install:"
    echo "   1. Transfer to Android"
    echo "   2. Enable 'Unknown sources'"
    echo "   3. Install"
    echo ""
    echo "💻 Copy to Windows:"
    echo "   cp '$APK_FILE' '/mnt/c/Users/FALCON/Desktop/'"
else
    echo "❌ APK not found."
    echo ""
    echo "Last errors from log:"
    tail -50 build.log | grep -i "error\|fail\|exception\|missing" | head -20
fi
