#import <UIKit/UIKit.h>
#import <Preferences/PSListController.h>
#import <Preferences/PSSpecifier.h>

@interface TSListControllerShared : PSListController
- (BOOL)isAxiomBox;
- (NSString*)getAxiomBoxVersion;
- (void)downloadAxiomBoxAndRun:(void (^)(NSString* localAxiomBoxTarPath))doHandler;
- (void)installAxiomBoxPressed;
- (void)updateAxiomBoxPressed;
- (void)rebuildIconCachePressed;
- (void)refreshAppRegistrationsPressed;
- (void)uninstallPersistenceHelperPressed;
- (void)handleUninstallation;
- (NSMutableArray*)argsForUninstallingAxiomBox;
- (void)uninstallAxiomBoxPressed;
@end