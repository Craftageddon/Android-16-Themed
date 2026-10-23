package com.craftageddon.thor.integration;
import android.service.quicksettings.Tile;
import android.service.quicksettings.TileService;
import android.graphics.drawable.Icon;
/** Actual SystemUI extension; it changes only this app's selected control state. */
public final class ForgeTileService extends TileService {
    @Override public void onStartListening(){super.onStartListening();update();}
    @Override public void onClick(){super.onClick();SelectionStore.set(this,!SelectionStore.get(this));update();}
    private void update(){
        Tile tile=getQsTile();if(tile==null)return;
        boolean selected=SelectionStore.get(this);
        tile.setLabel(getString(R.string.tile_label));
        tile.setSubtitle(getString(selected?R.string.state_on:R.string.state_off));
        tile.setContentDescription(getString(R.string.tile_label)+", "+getString(selected?R.string.state_on:R.string.state_off));
        tile.setState(selected?Tile.STATE_ACTIVE:Tile.STATE_INACTIVE);
        tile.setIcon(Icon.createWithResource(this,R.drawable.cg_app_forge_monochrome));
        tile.updateTile();
    }
}
