#pragma once

#include "Modules/ModuleManager.h"

class FUAssetRevisionHistoryModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    void RegisterMenus();
    void OpenRevisionHistoryForSelectedAssets(const struct FToolMenuContext& Context) const;
};
