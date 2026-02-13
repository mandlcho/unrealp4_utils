#include "UAssetRevisionHistoryModule.h"

#include "ContentBrowserMenuContexts.h"
#include "Misc/PackageName.h"
#include "Misc/Paths.h"
#include "SourceControlWindows.h"
#include "ToolMenuSection.h"
#include "ToolMenus.h"

void FUAssetRevisionHistoryModule::StartupModule()
{
    UToolMenus::RegisterStartupCallback(
        FSimpleMulticastDelegate::FDelegate::CreateRaw(this, &FUAssetRevisionHistoryModule::RegisterMenus));
}

void FUAssetRevisionHistoryModule::ShutdownModule()
{
    if (UToolMenus::IsToolMenusAvailable())
    {
        UToolMenus::UnregisterOwner(this);
    }
}

void FUAssetRevisionHistoryModule::RegisterMenus()
{
}

void FUAssetRevisionHistoryModule::OpenRevisionHistoryForSelectedAssets(const FToolMenuContext& Context) const
{
    const UContentBrowserAssetContextMenuContext* AssetContext =
        Context.FindContext<UContentBrowserAssetContextMenuContext>();
    if (!AssetContext)
    {
        return;
    }

    TArray<FString> PackageFilenames;
    PackageFilenames.Reserve(AssetContext->SelectedAssets.Num());

    for (const FAssetData& AssetData : AssetContext->SelectedAssets)
    {
        const FString PackageName = AssetData.PackageName.ToString();

        FString PackageFilename;
        if (FPackageName::TryConvertLongPackageNameToFilename(
                PackageName,
                PackageFilename,
                FPackageName::GetAssetPackageExtension()))
        {
            PackageFilenames.Add(FPaths::ConvertRelativePathToFull(PackageFilename));
        }
    }

    if (PackageFilenames.Num() > 0)
    {
        FSourceControlWindows::DisplayRevisionHistory(PackageFilenames);
    }
}

IMPLEMENT_MODULE(FUAssetRevisionHistoryModule, UAssetRevisionHistory)
