export EMBEDDED_ROOT_HELPER ?= 0
export LEGACY_CT_BUG ?= 0

TARGET := iphone:clang:16.5:14.0
INSTALL_TARGET_PROCESSES = AxiomBoxHelper

ifdef CUSTOM_ARCHS
ARCHS = $(CUSTOM_ARCHS)
else
ARCHS = arm64
endif

ifneq ($(LEGACY_CT_BUG),1)
TARGET_CODESIGN = ../Exploits/fastPathSign/fastPathSign
endif

include $(THEOS)/makefiles/common.mk

APPLICATION_NAME = AxiomBoxHelper

AxiomBoxHelper_FILES = $(wildcard *.m) $(wildcard ../Shared/*.m)
AxiomBoxHelper_FRAMEWORKS = UIKit CoreGraphics CoreServices CoreTelephony
AxiomBoxHelper_PRIVATE_FRAMEWORKS = Preferences MobileContainerManager
AxiomBoxHelper_CFLAGS = -fobjc-arc -I../Shared -I$(shell brew --prefix)/opt/libarchive/include

ifeq ($(LEGACY_CT_BUG),1)
AxiomBoxHelper_CODESIGN_FLAGS = -Sentitlements.plist -K../legacy.p12
AxiomBoxHelper_CFLAGS += -DLEGACY_CT_BUG=1
else
AxiomBoxHelper_CODESIGN_FLAGS = --entitlements entitlements.plist
endif

ifeq ($(EMBEDDED_ROOT_HELPER),1)
AxiomBoxHelper_CFLAGS += -DEMBEDDED_ROOT_HELPER=1
AxiomBoxHelper_FILES += $(wildcard ../RootHelper/*.m)
AxiomBoxHelper_LIBRARIES += archive
AxiomBoxHelper_PRIVATE_FRAMEWORKS += SpringBoardServices BackBoardServices FrontBoardServices
endif

include $(THEOS_MAKE_PATH)/application.mk