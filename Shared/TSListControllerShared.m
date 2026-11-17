#import "TSListControllerShared.h"
#import "TSUtil.h"
#import "TSPresentationDelegate.h"

@implementation TSListControllerShared

- (BOOL)isAxiomBox
{
	return YES;
}

- (NSString*)getAxiomBoxVersion
{
	if([self isAxiomBox])
	{
		return [NSBundle.mainBundle objectForInfoDictionaryKey:@"CFBundleVersion"];
	}
	else
	{
		NSString* trollStorePath = trollStoreAppPath();
		if(!trollStorePath) return nil;

		NSBundle* trollStoreBundle = [NSBundle bundleWithPath:trollStorePath];
		return [trollStoreBundle objectForInfoDictionaryKey:@"CFBundleVersion"];
	}
}

- (void)downloadAxiomBoxAndRun:(void (^)(NSString* localAxiomBoxTarPath))doHandler
{
	NSURL* trollStoreURL = [NSURL URLWithString:@"https://github.com/axiomdev/AxiomBox/releases/latest/download/AxiomBox.tar"];
	NSURLRequest* trollStoreRequest = [NSURLRequest requestWithURL:trollStoreURL];

	NSURLSessionDownloadTask* downloadTask = [NSURLSession.sharedSession downloadTaskWithRequest:trollStoreRequest completionHandler:^(NSURL *location, NSURLResponse *response, NSError *error)
	{
		if(error)
		{
			UIAlertController* errorAlert = [UIAlertController alertControllerWithTitle:@"Error" message:[NSString stringWithFormat:@"Error downloading AxiomBox: %@", error] preferredStyle:UIAlertControllerStyleAlert];
			UIAlertAction* closeAction = [UIAlertAction actionWithTitle:@"Close" style:UIAlertActionStyleDefault handler:nil];
			[errorAlert addAction:closeAction];

			dispatch_async(dispatch_get_main_queue(), ^
			{
				[TSPresentationDelegate stopActivityWithCompletion:^
				{
					[TSPresentationDelegate presentViewController:errorAlert animated:YES completion:nil];
				}];
			});
		}
		else
		{
			NSString* tarTmpPath = [NSTemporaryDirectory() stringByAppendingPathComponent:@"AxiomBox.tar"];
			[[NSFileManager defaultManager] removeItemAtPath:tarTmpPath error:nil];
			[[NSFileManager defaultManager] copyItemAtPath:location.path toPath:tarTmpPath error:nil];

			doHandler(tarTmpPath);
		}
	}];

	[downloadTask resume];
}

- (void)_installAxiomBoxComingFromUpdateFlow:(BOOL)update
{
	if(update)
	{
		[TSPresentationDelegate startActivity:@"Updating AxiomBox"];
	}
	else
	{
		[TSPresentationDelegate startActivity:@"Installing AxiomBox"];
	}

	[self downloadAxiomBoxAndRun:^(NSString* tmpTarPath)
	{
		int ret = spawnRoot(rootHelperPath(), @[@"install-axiombox", tmpTarPath], nil, nil);
		[[NSFileManager defaultManager] removeItemAtPath:tmpTarPath error:nil];

		if(ret == 0)
		{
			respring();

			if([self isAxiomBox])
			{
				exit(0);
			}
			else
			{
				dispatch_async(dispatch_get_main_queue(), ^
				{
					[TSPresentationDelegate stopActivityWithCompletion:^
					{
						[self reloadSpecifiers];
					}];
				});
			}
		}
		else
		{
			dispatch_async(dispatch_get_main_queue(), ^
			{
				[TSPresentationDelegate stopActivityWithCompletion:^
				{
					UIAlertController* errorAlert = [UIAlertController alertControllerWithTitle:@"Error" message:[NSString stringWithFormat:@"Error installing AxiomBox: axiomboxhelper returned %d", ret] preferredStyle:UIAlertControllerStyleAlert];
					UIAlertAction* closeAction = [UIAlertAction actionWithTitle:@"Close" style:UIAlertActionStyleDefault handler:nil];
					[errorAlert addAction:closeAction];
					[TSPresentationDelegate presentViewController:errorAlert animated:YES completion:nil];
				}];
			});
		}
	}];
}

- (void)installAxiomBoxPressed
{
	[self _installAxiomBoxComingFromUpdateFlow:NO];
}

- (void)updateAxiomBoxPressed
{
	[self _installAxiomBoxComingFromUpdateFlow:YES];
}

- (void)rebuildIconCachePressed
{
	[TSPresentationDelegate startActivity:@"Rebuilding Icon Cache"];

	dispatch_async(dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0), ^
	{
		spawnRoot(rootHelperPath(), @[@"refresh-all"], nil, nil);

		dispatch_async(dispatch_get_main_queue(), ^
		{
			[TSPresentationDelegate stopActivityWithCompletion:nil];
		});
	});
}

- (void)refreshAppRegistrationsPressed
{
	[TSPresentationDelegate startActivity:@"Refreshing"];

	dispatch_async(dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0), ^
	{
		spawnRoot(rootHelperPath(), @[@"refresh"], nil, nil);
		respring();

		dispatch_async(dispatch_get_main_queue(), ^
		{
			[TSPresentationDelegate stopActivityWithCompletion:nil];
		});
	});
}

- (void)uninstallPersistenceHelperPressed
{
	if([self isAxiomBox])
	{
		spawnRoot(rootHelperPath(), @[@"uninstall-persistence-helper"], nil, nil);
		[self reloadSpecifiers];
	}
	else
	{
		UIAlertController* uninstallWarningAlert = [UIAlertController alertControllerWithTitle:@"Warning" message:@"Uninstalling the persistence helper will revert this app back to it's original state, you will however no longer be able to persistently refresh the AxiomBox app registrations. Continue?" preferredStyle:UIAlertControllerStyleAlert];
	
		UIAlertAction* cancelAction = [UIAlertAction actionWithTitle:@"Cancel" style:UIAlertActionStyleCancel handler:nil];
		[uninstallWarningAlert addAction:cancelAction];

		UIAlertAction* continueAction = [UIAlertAction actionWithTitle:@"Continue" style:UIAlertActionStyleDestructive handler:^(UIAlertAction* action)
		{
			spawnRoot(rootHelperPath(), @[@"uninstall-persistence-helper"], nil, nil);
			exit(0);
		}];
		[uninstallWarningAlert addAction:continueAction];

		[TSPresentationDelegate presentViewController:uninstallWarningAlert animated:YES completion:nil];
	}
}

- (void)handleUninstallation
{
	if([self isAxiomBox])
	{
		exit(0);
	}
	else
	{
		[self reloadSpecifiers];
	}
}

- (NSMutableArray*)argsForUninstallingAxiomBox
{
	return @[@"uninstall-axiombox"].mutableCopy;
}

- (void)uninstallAxiomBoxPressed
{
	UIAlertController* uninstallAlert = [UIAlertController alertControllerWithTitle:@"Uninstall" message:@"You are about to uninstall AxiomBox, do you want to preserve the apps installed by it?" preferredStyle:UIAlertControllerStyleAlert];
	
	UIAlertAction* uninstallAllAction = [UIAlertAction actionWithTitle:@"Uninstall AxiomBox, Uninstall Apps" style:UIAlertActionStyleDestructive handler:^(UIAlertAction* action)
	{
		NSMutableArray* args = [self argsForUninstallingAxiomBox];
		spawnRoot(rootHelperPath(), args, nil, nil);
		[self handleUninstallation];
	}];
	[uninstallAlert addAction:uninstallAllAction];

	UIAlertAction* preserveAppsAction = [UIAlertAction actionWithTitle:@"Uninstall AxiomBox, Preserve Apps" style:UIAlertActionStyleDestructive handler:^(UIAlertAction* action)
	{
		NSMutableArray* args = [self argsForUninstallingAxiomBox];
		[args addObject:@"preserve-apps"];
		spawnRoot(rootHelperPath(), args, nil, nil);
		[self handleUninstallation];
	}];
	[uninstallAlert addAction:preserveAppsAction];

	UIAlertAction* cancelAction = [UIAlertAction actionWithTitle:@"Cancel" style:UIAlertActionStyleCancel handler:nil];
	[uninstallAlert addAction:cancelAction];

	[TSPresentationDelegate presentViewController:uninstallAlert animated:YES completion:nil];
}

@end