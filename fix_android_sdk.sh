#!/bin/bash
echo "=== COMPLETE ANDROID SDK FIX ==="

# 1. Clean everything
rm -rf ~/.buildozer
rm -rf ~/.android
rm -rf ~/android-sdk

# 2. Create fresh directories
mkdir -p ~/.buildozer/android/platform/android-sdk
cd ~/.buildozer/android/platform/android-sdk

# 3. Download SDK tools
echo "Downloading Android SDK..."
wget -q https://dl.google.com/android/repository/commandlinetools-linux-9477386_latest.zip
unzip -q commandlinetools-linux-9477386_latest.zip
rm commandlinetools-linux-9477386_latest.zip

# 4. Fix directory structure
mv cmdline-tools latest
mkdir -p cmdline-tools
mv latest cmdline-tools/

# 5. Set paths
export ANDROID_SDK_ROOT=~/.buildozer/android/platform/android-sdk
export ANDROID_HOME=$ANDROID_SDK_ROOT
export PATH=$PATH:$ANDROID_SDK_ROOT/cmdline-tools/latest/bin

# 6. Accept ALL licenses
mkdir -p ~/.android/licenses
cat > ~/.android/licenses/android-sdk-license << LICENSE
8933bad161af4178b1185d1a37fbf41ea5269c55
d56f5187479451eabf01fb78af6dfcb131a6481e
24333f8a63b6825ea9c5514f83c2829b004d1fee
LICENSE

# 7. Install required components
echo "Installing Android build-tools 33.0.0..."
yes | sdkmanager --sdk_root=$ANDROID_SDK_ROOT "build-tools;33.0.0"
echo "Installing platform-tools..."
yes | sdkmanager --sdk_root=$ANDROID_SDK_ROOT "platform-tools"
echo "Installing Android API 33..."
yes | sdkmanager --sdk_root=$ANDROID_SDK_ROOT "platforms;android-33"

# 8. Verify installation
echo "Verifying aidl..."
AIDL_PATH=$(find $ANDROID_SDK_ROOT -name "aidl" -type f | head -1)
if [ -f "$AIDL_PATH" ]; then
    echo "✅ aidl found: $AIDL_PATH"
    ls -la $ANDROID_SDK_ROOT/build-tools/33.0.0/aidl*
else
    echo "❌ aidl NOT found"
    echo "Build-tools contents:"
    ls -la $ANDROID_SDK_ROOT/build-tools/33.0.0/ 2>/dev/null || echo "No build-tools directory"
fi

# 9. Create symlink for buildozer
mkdir -p $ANDROID_SDK_ROOT/tools/bin
ln -sf $ANDROID_SDK_ROOT/cmdline-tools/latest/bin/sdkmanager $ANDROID_SDK_ROOT/tools/bin/sdkmanager 2>/dev/null

echo "=== SDK FIX COMPLETE ==="
