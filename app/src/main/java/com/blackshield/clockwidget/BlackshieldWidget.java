package com.blackshield.clockwidget;

import android.app.AlarmManager;
import android.app.PendingIntent;
import android.appwidget.AppWidgetManager;
import android.appwidget.AppWidgetProvider;
import android.content.Context;
import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.graphics.Paint;
import android.graphics.Typeface;
import android.text.format.DateFormat;
import android.widget.RemoteViews;

import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Date;
import java.util.Locale;

/**
 * Blackshield Mercenary clock widget — bitmap-rendered edition.
 *
 * The whole face (gothic time, blood divider, steel date) is drawn onto a
 * Bitmap here in our own process, where the bundled Pirata One typeface is
 * guaranteed to load. The host launcher only ever sees a plain ImageView.
 * Minute ticks come from a self-rescheduling alarm aligned to the minute.
 */
public class BlackshieldWidget extends AppWidgetProvider {

    private static final String ACTION_TICK = "com.blackshield.clockwidget.TICK";

    private static final int COLOR_TIME = 0xFFE8E6E3;  // bone white
    private static final int COLOR_BLOOD = 0xFFC1121F; // the blood line
    private static final int COLOR_STEEL = 0xFF9BA0A6; // cold steel gray

    private static final int BMP_W = 900;
    private static final int BMP_H = 420;

    @Override
    public void onUpdate(Context context, AppWidgetManager appWidgetManager, int[] appWidgetIds) {
        renderAll(context, appWidgetManager, appWidgetIds);
        scheduleNextMinute(context);
    }

    @Override
    public void onReceive(Context context, Intent intent) {
        super.onReceive(context, intent);
        String action = intent.getAction();
        if (ACTION_TICK.equals(action)
                || Intent.ACTION_TIME_CHANGED.equals(action)
                || Intent.ACTION_DATE_CHANGED.equals(action)
                || Intent.ACTION_TIMEZONE_CHANGED.equals(action)
                || Intent.ACTION_BOOT_COMPLETED.equals(action)) {
            AppWidgetManager mgr = AppWidgetManager.getInstance(context);
            int[] ids = mgr.getAppWidgetIds(
                    new android.content.ComponentName(context, BlackshieldWidget.class));
            if (ids.length > 0) {
                renderAll(context, mgr, ids);
                scheduleNextMinute(context);
            }
        }
    }

    @Override
    public void onDisabled(Context context) {
        AlarmManager am = (AlarmManager) context.getSystemService(Context.ALARM_SERVICE);
        am.cancel(tickIntent(context));
    }

    private void renderAll(Context context, AppWidgetManager mgr, int[] ids) {
        Bitmap face = drawFace(context);
        for (int id : ids) {
            RemoteViews views = new RemoteViews(context.getPackageName(), R.layout.widget_blackshield);
            views.setImageViewBitmap(R.id.widget_canvas, face);
            mgr.updateAppWidget(id, views);
        }
    }

    private Bitmap drawFace(Context context) {
        Bitmap bmp = Bitmap.createBitmap(BMP_W, BMP_H, Bitmap.Config.ARGB_8888);
        Canvas canvas = new Canvas(bmp);

        Typeface gothic = Typeface.createFromAsset(context.getAssets(), "pirata_one.ttf");

        boolean is24h = DateFormat.is24HourFormat(context);
        String time = new SimpleDateFormat(is24h ? "HH:mm" : "h:mm", Locale.getDefault())
                .format(new Date());
        String date = new SimpleDateFormat("EEEE, MMMM d", Locale.getDefault())
                .format(new Date()).toUpperCase(Locale.getDefault());

        float cx = BMP_W / 2f;

        // Time — Pirata One, bone white
        Paint timePaint = new Paint(Paint.ANTI_ALIAS_FLAG | Paint.SUBPIXEL_TEXT_FLAG);
        timePaint.setTypeface(gothic);
        timePaint.setColor(COLOR_TIME);
        timePaint.setTextSize(190f);
        timePaint.setTextAlign(Paint.Align.CENTER);
        timePaint.setShadowLayer(8f, 0f, 3f, 0xFF000000);

        Paint.FontMetrics fm = timePaint.getFontMetrics();
        float timeBaseline = BMP_H * 0.44f - (fm.ascent + fm.descent) / 2f;
        canvas.drawText(time, cx, timeBaseline, timePaint);

        // The blood line
        float lineW = BMP_W * 0.34f;
        float lineY = BMP_H * 0.60f;
        Paint linePaint = new Paint(Paint.ANTI_ALIAS_FLAG);
        linePaint.setColor(COLOR_BLOOD);
        canvas.drawRect(cx - lineW / 2f, lineY, cx + lineW / 2f, lineY + 5f, linePaint);

        // Date — Pirata One, steel gray, letterspaced caps
        Paint datePaint = new Paint(Paint.ANTI_ALIAS_FLAG | Paint.SUBPIXEL_TEXT_FLAG);
        datePaint.setTypeface(gothic);
        datePaint.setColor(COLOR_STEEL);
        datePaint.setTextSize(58f);
        datePaint.setTextAlign(Paint.Align.CENTER);
        datePaint.setLetterSpacing(0.10f);
        datePaint.setShadowLayer(5f, 0f, 2f, 0xFF000000);
        canvas.drawText(date, cx, BMP_H * 0.82f, datePaint);

        return bmp;
    }

    private void scheduleNextMinute(Context context) {
        AlarmManager am = (AlarmManager) context.getSystemService(Context.ALARM_SERVICE);
        Calendar next = Calendar.getInstance();
        next.add(Calendar.MINUTE, 1);
        next.set(Calendar.SECOND, 0);
        next.set(Calendar.MILLISECOND, 300);
        PendingIntent pi = tickIntent(context);
        // USE_EXACT_ALARM is declared in the manifest (auto-granted at install),
        // so the exact path should always succeed. Keep the runtime check anyway:
        // the user can still revoke Alarms & reminders on Android 14+.
        boolean canExact = android.os.Build.VERSION.SDK_INT < 31 || am.canScheduleExactAlarms();
        if (canExact) {
            am.setExactAndAllowWhileIdle(AlarmManager.RTC, next.getTimeInMillis(), pi);
        } else {
            // Exact-alarm permission revoked — degrade to inexact and tell the user
            // to re-enable Settings → Apps → Blackshield Clock → Alarms & reminders.
            try {
                am.setAndAllowWhileIdle(AlarmManager.RTC, next.getTimeInMillis(), pi);
            } catch (SecurityException ignored) { }
        }
    }

    private PendingIntent tickIntent(Context context) {
        Intent i = new Intent(context, BlackshieldWidget.class);
        i.setAction(ACTION_TICK);
        return PendingIntent.getBroadcast(context, 0, i,
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
    }
}
