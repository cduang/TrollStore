TARGET := iphone:clang:16.5:14.0
INSTALL_TARGET_PROCESSES = AxiomBoxLite
ARCHS = arm64

include $(THEOS)/makefiles/common.mk

APPLICATION_NAME = AxiomBoxLite

AxiomBoxLite_FILES = $(wildcard ../TrollStore/*.m) $(wildcard ../Shared/*.m)
AxiomBoxLite_FRAMEWORKS = UIKit CoreGraphics CoreServices CoreTelephony
AxiomBoxLite_PRIVATE_FRAMEWORKS = Preferences MobileIcons MobileContainerManager
AxiomBoxLite_LIBRARIES = archive
AxiomBoxLite_CFLAGS = -fobjc-arc -I../Shared -I$(shell brew --prefix)/opt/libarchive/include -DTROLLSTORE_LITE
AxiomBoxLite_CODESIGN_FLAGS = -Sentitlements.plist

include $(THEOS_MAKE_PATH)/application.mk
