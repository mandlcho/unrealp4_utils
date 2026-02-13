using UnrealBuildTool;

public class UAssetRevisionHistory : ModuleRules
{
    public UAssetRevisionHistory(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

        PublicDependencyModuleNames.AddRange(new[]
        {
            "Core",
            "CoreUObject",
            "Engine"
        });

        PrivateDependencyModuleNames.AddRange(new[]
        {
            "UnrealEd",
            "ToolMenus",
            "ContentBrowser",
            "SourceControl",
            "SourceControlWindows"
        });
    }
}
