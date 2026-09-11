package com.blackshield.clockwidget;

import android.app.Activity;
import android.os.Bundle;
import android.view.ViewGroup;
import android.widget.ImageView;

/**
 * Launcher entry: renders the exact widget face full-screen.
 * Gives the app drawer icon somewhere to land, shows users what the
 * widget looks like, and doubles as the previewImage capture harness.
 */
public class PreviewActivity extends Activity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        ImageView iv = new ImageView(this);
        iv.setImageBitmap(new BlackshieldWidget().drawFace(this));
        iv.setScaleType(ImageView.ScaleType.FIT_CENTER);
        iv.setAdjustViewBounds(true);
        iv.setBackgroundColor(0xFF101014); // steel tile dark
        iv.setLayoutParams(new ViewGroup.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT));
        setContentView(iv);
    }
}
