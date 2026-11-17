TARGET := iphone:clang:16.5:14.0
INSTALL_TARGET_PROCESSES = AxiomBox
ARCHS = arm64

TARGET_CODESIGN = ../Exploits/fastPathSign/fastPathSign

include $(THEOS)/makefiles/common.mk

APPLICATION_NAME = AxiomBox

AxiomBox_FILES = $(wildcard *.m) $(wildcard ../Shared/*.m)
AxiomBox_FRAMEWORKS = UIKit CoreGraphics CoreServices CoreTelephony
AxiomBox_PRIVATE_FRAMEWORKS = Preferences MobileIcons MobileContainerManager
AxiomBox_LIBRARIES = archive
AxiomBox_CFLAGS = -fobjc-arc -I../Shared -I$(shell brew --prefix)/opt/libarchive/include
AxiomBox_CODESIGN_FLAGS = --entitlements entitlements.plist

include $(THEOS_MAKE_PATH)/application.mk
