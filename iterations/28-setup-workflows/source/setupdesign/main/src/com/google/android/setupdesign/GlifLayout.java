/*
 * Copyright (C) 2015 The Android Open Source Project
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package com.google.android.setupdesign;

import android.annotation.TargetApi;
import android.app.Activity;
import android.content.ActivityNotFoundException;
import android.content.Context;
import android.content.Intent;
import android.content.res.ColorStateList;
import android.content.res.Resources.Theme;
import android.content.res.TypedArray;
import android.graphics.Color;
import android.graphics.drawable.ColorDrawable;
import android.graphics.drawable.Drawable;
import android.os.Build;
import android.os.Build.VERSION;
import android.os.Build.VERSION_CODES;
import android.os.Parcel;
import android.os.Parcelable;
import android.os.PersistableBundle;
import android.util.AttributeSet;
import android.util.TypedValue;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.view.ViewStub;
import android.view.ViewTreeObserver;
import android.view.WindowInsets;
import android.widget.ImageButton;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.ScrollView;
import android.widget.TextView;
import androidx.annotation.AttrRes;
import androidx.annotation.ColorInt;
import androidx.annotation.LayoutRes;
import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.annotation.StringRes;
import androidx.annotation.VisibleForTesting;
import androidx.core.view.WindowInsetsCompat;
import androidx.core.view.insets.GradientProtection;
import androidx.core.view.insets.Protection;
import androidx.core.view.insets.ProtectionLayout;
import androidx.window.embedding.ActivityEmbeddingController;
import com.google.android.setupcompat.PartnerCustomizationLayout;
import com.google.android.setupcompat.logging.CustomEvent;
import com.google.android.setupcompat.logging.MetricKey;
import com.google.android.setupcompat.logging.SetupMetricsLogger;
import com.google.android.setupcompat.partnerconfig.PartnerConfig;
import com.google.android.setupcompat.partnerconfig.PartnerConfigHelper;
import com.google.android.setupcompat.template.FooterBarMixin;
import com.google.android.setupcompat.template.StatusBarMixin;
import com.google.android.setupcompat.template.SystemNavBarMixin;
import com.google.android.setupcompat.util.ForceTwoPaneHelper;
import com.google.android.setupcompat.util.KeyboardHelper;
import com.google.android.setupcompat.util.Logger;
import com.google.android.setupcompat.util.WizardManagerHelper;
import com.google.android.setupcompat.view.ButtonBarLayout;
import com.google.android.setupdesign.template.DescriptionMixin;
import com.google.android.setupdesign.template.FloatingActionButtonMixin;
import com.google.android.setupdesign.template.FloatingBackButtonMixin;
import com.google.android.setupdesign.template.FloatingSetupProgressIndicatorMixin;
import com.google.android.setupdesign.template.HeaderMixin;
import com.google.android.setupdesign.template.IconMixin;
import com.google.android.setupdesign.template.IllustrationProgressMixin;
import com.google.android.setupdesign.template.ProfileMixin;
import com.google.android.setupdesign.template.ProgressBarMixin;
import com.google.android.setupdesign.template.RequireScrollMixin;
import com.google.android.setupdesign.template.ScrollViewScrollHandlingDelegate;
import com.google.android.setupdesign.util.DescriptionStyler;
import com.google.android.setupdesign.util.ItemStyler;
import com.google.android.setupdesign.util.LayoutStyler;
import com.google.android.setupdesign.util.ThemeHelper;
import java.util.ArrayList;
import java.util.Optional;

/**
 * Layout for the GLIF theme used in Setup Wizard for N.
 *
 * <p>Example usage:
 *
 * <pre>{@code
 * &lt;com.google.android.setupdesign.GlifLayout
 *     xmlns:android="http://schemas.android.com/apk/res/android"
 *     xmlns:app="http://schemas.android.com/apk/res-auto"
 *     android:layout_width="match_parent"
 *     android:layout_height="match_parent"
 *     android:icon="@drawable/my_icon"
 *     app:sucHeaderText="@string/my_title">
 *
 *     &lt;!-- Content here -->
 *
 * &lt;/com.google.android.setupdesign.GlifLayout>
 * }</pre>
 */
public class GlifLayout extends PartnerCustomizationLayout {
  private static final Logger LOG = new Logger(GlifLayout.class);
  private ColorStateList primaryColor;
  private boolean backgroundPatterned = true;
  private boolean applyPartnerHeavyThemeResource = false;

  private static final int ACCESSIBILITY_SETTINGS_REQUEST_CODE = 101;

  @VisibleForTesting
  ViewTreeObserver.OnScrollChangedListener onScrollChangedListener =
      new ViewTreeObserver.OnScrollChangedListener() {
        @Override
        public void onScrollChanged() {
          updateScrollState();
        }
      };

  private ViewTreeObserver.OnGlobalLayoutListener onGlobalLayoutListener =
      new ViewTreeObserver.OnGlobalLayoutListener() {
        @Override
        public void onGlobalLayout() {
          updateScrollState();
        }
      };

  /** The color of the background. If null, the color will inherit from primaryColor. */
  @Nullable private ColorStateList backgroundBaseColor;

  public GlifLayout(Context context) {
    this(context, 0, 0);
  }

  public GlifLayout(Context context, int template) {
    this(context, template, 0);
  }

  public GlifLayout(Context context, int template, int containerId) {
    super(context, template, containerId);
    init(null, R.attr.sudLayoutTheme);
  }

  public GlifLayout(Context context, AttributeSet attrs) {
    super(context, attrs);
    init(attrs, R.attr.sudLayoutTheme);
  }

  @TargetApi(VERSION_CODES.HONEYCOMB)
  public GlifLayout(Context context, AttributeSet attrs, int defStyleAttr) {
    super(context, attrs, defStyleAttr);
    init(attrs, defStyleAttr);
  }

  // All the constructors delegate to this init method. The 3-argument constructor is not
  // available in LinearLayout before v11, so call super with the exact same arguments.
  private void init(AttributeSet attrs, int defStyleAttr) {
    if (isInEditMode()) {
      return;
    }
    TypedArray a =
        getContext().obtainStyledAttributes(attrs, R.styleable.SudGlifLayout, defStyleAttr, 0);
    boolean usePartnerHeavyTheme =
        a.getBoolean(R.styleable.SudGlifLayout_sudUsePartnerHeavyTheme, false);
    applyPartnerHeavyThemeResource = shouldApplyPartnerResource() && usePartnerHeavyTheme;
    registerMixin(HeaderMixin.class, new HeaderMixin(this, attrs, defStyleAttr));
    registerMixin(DescriptionMixin.class, new DescriptionMixin(this, attrs, defStyleAttr));
    registerMixin(IconMixin.class, new IconMixin(this, attrs, defStyleAttr));
    registerMixin(ProfileMixin.class, new ProfileMixin(this, attrs, defStyleAttr));
    registerMixin(ProgressBarMixin.class, new ProgressBarMixin(this, attrs, defStyleAttr));
    registerMixin(IllustrationProgressMixin.class, new IllustrationProgressMixin(this));
    registerMixin(
        FloatingBackButtonMixin.class, new FloatingBackButtonMixin(this, attrs, defStyleAttr));
    registerMixin(
        FloatingActionButtonMixin.class, new FloatingActionButtonMixin(this, attrs, defStyleAttr));
    registerMixin(
        FloatingSetupProgressIndicatorMixin.class,
        new FloatingSetupProgressIndicatorMixin(this, attrs, defStyleAttr));
    final RequireScrollMixin requireScrollMixin = new RequireScrollMixin(this);
    registerMixin(RequireScrollMixin.class, requireScrollMixin);
    final ScrollView scrollView = getScrollView();
    if (scrollView != null) {
      requireScrollMixin.setScrollHandlingDelegate(
          new ScrollViewScrollHandlingDelegate(requireScrollMixin, scrollView));
    }
    ColorStateList primaryColor = a.getColorStateList(R.styleable.SudGlifLayout_sudColorPrimary);
    if (primaryColor != null) {
      setPrimaryColor(primaryColor);
    }
    if (shouldApplyPartnerHeavyThemeResource()) {
      updateContentBackgroundColorWithPartnerConfig();
    }
    View view = findManagedViewById(R.id.sud_layout_content);
    if (view != null) {
      if (shouldApplyPartnerResource()) {
        // The margin of content is defined by @style/SudContentFrame. The Setupdesign library
        // cannot obtain the content resource ID of the client, so the value of the content margin
        // cannot be adjusted through GlifLayout. If the margin sides are changed through the
        // partner config, it can only be based on the increased or decreased value to adjust the
        // value of padding. In this way, the value of content margin plus padding will be equal to
        // the value of partner config.
        LayoutStyler.applyPartnerCustomizationExtraPaddingStyle(view);
      }
      // {@class GlifPreferenceLayout} Inherited from {@class GlifRecyclerLayout}. The API would
      // be called twice from GlifRecyclerLayout and GlifLayout, so it should skip the API here
      // when the instance is GlifPreferenceLayout.
      if (!(this instanceof GlifPreferenceLayout)) {
        tryApplyPartnerCustomizationContentPaddingTopStyle(view);
      }
    }
    updateLandscapeMiddleHorizontalSpacing();
    updateViewFocusable();
    ColorStateList backgroundColor =
        a.getColorStateList(R.styleable.SudGlifLayout_sudBackgroundBaseColor);
    setBackgroundBaseColor(backgroundColor);
    boolean backgroundPatterned =
        a.getBoolean(R.styleable.SudGlifLayout_sudBackgroundPatterned, true);
    setBackgroundPatterned(backgroundPatterned);
    final int stickyHeader = a.getResourceId(R.styleable.SudGlifLayout_sudStickyHeader, 0);
    if (stickyHeader != 0) {
      inflateStickyHeader(stickyHeader);
    }
    if (PartnerConfigHelper.isGlifExpressiveEnabled(getContext())) {
      initScrollingListener();
      View protection = findViewById(R.id.sud_layout_protection);
      if (protection != null
          && protection instanceof ProtectionLayout protectionLayout
          && backgroundBaseColor != null) {
        ArrayList<Protection> list = new ArrayList<>();
        list.add(
            new GradientProtection(
                WindowInsetsCompat.Side.TOP, backgroundBaseColor.getDefaultColor()));
        protectionLayout.setProtections(list);
      }
    }
    initBackButton();
    initAccessibilityButton();
    initialLogging();
    a.recycle();
  }

  private void updateScrollState() {
    Optional<Boolean> canWholeViewsScrollDown = canWholeViewsScrollDown();
    if (canWholeViewsScrollDown.isPresent()) {
      onScrolling(!canWholeViewsScrollDown.get());
    }
  }

  private void initialLogging() {
    if (activity != null) {
      LOG.atInfo(
          "Using setup design "
              + this.getClass().getSimpleName()
              + " to init for "
              + activity.getClass().getSimpleName());
    } else {
      LOG.atInfo(
          "Using setup design " + this.getClass().getSimpleName() + " to init for null activity");
    }
  }

  @Override
  protected void onFinishInflate() {
    super.onFinishInflate();
    getMixin(IconMixin.class).tryApplyPartnerCustomizationStyle();
    getMixin(HeaderMixin.class).tryApplyPartnerCustomizationStyle();
    getMixin(DescriptionMixin.class).tryApplyPartnerCustomizationStyle();
    getMixin(ProgressBarMixin.class).tryApplyPartnerCustomizationStyle();
    getMixin(ProfileMixin.class).tryApplyPartnerCustomizationStyle();
    getMixin(FloatingBackButtonMixin.class).tryApplyPartnerCustomizationStyle();
    tryApplyPartnerCustomizationStyleToShortDescription();
  }

  @Override
  protected Parcelable onSaveInstanceState() {
    Parcelable superState = super.onSaveInstanceState();
    GlifSavedState savedState = new GlifSavedState(superState);
    // save the state of the scroll to bottom
    savedState.everScrolledToBottom = getMixin(RequireScrollMixin.class).isEverScrolledToBottom();
    return savedState;
  }

  @Override
  protected void onRestoreInstanceState(Parcelable state) {
    if (!(state instanceof GlifSavedState savedState)) {
      super.onRestoreInstanceState(state);
      return;
    }
    super.onRestoreInstanceState(savedState.getSuperState());
    // assign the state of the scroll to bottom
    getMixin(RequireScrollMixin.class)
        .onRestoreEverScrolledToBottom(savedState.everScrolledToBottom);
  }

  static class GlifSavedState extends BaseSavedState {
    boolean everScrolledToBottom = false;

    GlifSavedState(Parcelable superState) {
      super(superState);
    }

    private GlifSavedState(Parcel in) {
      super(in);
      this.everScrolledToBottom = (in.readInt() == 1);
    }

    @Override
    public void writeToParcel(Parcel out, int flags) {
      super.writeToParcel(out, flags);
      out.writeInt(this.everScrolledToBottom ? 1 : 0);
    }

    public static final Parcelable.Creator<GlifSavedState> CREATOR =
        new Parcelable.Creator<GlifSavedState>() {
          @Override
          public GlifSavedState createFromParcel(Parcel in) {
            return new GlifSavedState(in);
          }

          @Override
          public GlifSavedState[] newArray(int size) {
            return new GlifSavedState[size];
          }
        };
  }

  private void updateViewFocusable() {
    if (KeyboardHelper.isKeyboardFocusEnhancementEnabled(getContext())) {
      View headerView = this.findManagedViewById(R.id.sud_header_scroll_view);
      if (headerView != null) {
        headerView.setFocusable(false);
      }
      View view = this.findManagedViewById(R.id.sud_scroll_view);
      if (view != null) {
        view.setFocusable(false);
      }
    }
  }

  // TODO: remove when all sud_layout_description has migrated to
  // DescriptionMixin(sud_layout_subtitle)
  private void tryApplyPartnerCustomizationStyleToShortDescription() {
    TextView description = this.findManagedViewById(R.id.sud_layout_description);
    if (description != null) {
      if (applyPartnerHeavyThemeResource) {
        DescriptionStyler.applyPartnerCustomizationHeavyStyle(description);
      } else if (shouldApplyPartnerResource()) {
        DescriptionStyler.applyPartnerCustomizationLightStyle(description);
      }
    }
  }

  protected boolean canViewScrollDown(ScrollView scrollView) {
    if (scrollView == null) {
      // If the scroll view is null, it means the view is not scrollable. So we should return true
      // to indicate that the view is at the bottom.
      return false;
    }
    // direction > 0 means view can scroll down, direction < 0 means view can scroll
    // up. Here we use direction > 0 to detect whether the view can be scrolling down
    // or not.
    return scrollView != null && scrollView.canScrollVertically(/* direction= */ 1);
  }

  protected void updateLandscapeMiddleHorizontalSpacing() {
    int horizontalSpacing =
        getResources().getDimensionPixelSize(R.dimen.sud_glif_land_middle_horizontal_spacing);
    if (shouldApplyPartnerResource()
        && PartnerConfigHelper.get(getContext())
            .isPartnerConfigAvailable(PartnerConfig.CONFIG_LAND_MIDDLE_HORIZONTAL_SPACING)) {
      horizontalSpacing =
          (int)
              PartnerConfigHelper.get(getContext())
                  .getDimension(getContext(), PartnerConfig.CONFIG_LAND_MIDDLE_HORIZONTAL_SPACING);
    }
    View headerView = this.findManagedViewById(R.id.sud_landscape_header_area);
    if (headerView != null) {
      int layoutMarginEnd;
      if (shouldApplyPartnerResource()
          && PartnerConfigHelper.get(getContext())
              .isPartnerConfigAvailable(PartnerConfig.CONFIG_LAYOUT_MARGIN_END)) {
        layoutMarginEnd =
            (int)
                PartnerConfigHelper.get(getContext())
                    .getDimension(getContext(), PartnerConfig.CONFIG_LAYOUT_MARGIN_END);
      } else {
        TypedArray a = getContext().obtainStyledAttributes(new int[] {R.attr.sudMarginEnd});
        layoutMarginEnd = a.getDimensionPixelSize(0, 0);
        a.recycle();
      }
      int paddingEnd = (horizontalSpacing / 2) - layoutMarginEnd;
      if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.JELLY_BEAN_MR1) {
        headerView.setPaddingRelative(
            headerView.getPaddingStart(),
            headerView.getPaddingTop(),
            paddingEnd,
            headerView.getPaddingBottom());
      } else {
        headerView.setPadding(
            headerView.getPaddingLeft(),
            headerView.getPaddingTop(),
            paddingEnd,
            headerView.getPaddingBottom());
      }
    }
    View contentView = this.findManagedViewById(R.id.sud_landscape_content_area);
    if (contentView != null) {
      int layoutMarginStart;
      if (shouldApplyPartnerResource()
          && PartnerConfigHelper.get(getContext())
              .isPartnerConfigAvailable(PartnerConfig.CONFIG_LAYOUT_MARGIN_START)) {
        layoutMarginStart =
            (int)
                PartnerConfigHelper.get(getContext())
                    .getDimension(getContext(), PartnerConfig.CONFIG_LAYOUT_MARGIN_START);
      } else {
        TypedArray a = getContext().obtainStyledAttributes(new int[] {R.attr.sudMarginStart});
        layoutMarginStart = a.getDimensionPixelSize(0, 0);
        a.recycle();
      }
      int paddingStart = 0;
      if (headerView != null) {
        paddingStart = (horizontalSpacing / 2) - layoutMarginStart;
      }
      if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.JELLY_BEAN_MR1) {
        contentView.setPaddingRelative(
            paddingStart,
            contentView.getPaddingTop(),
            contentView.getPaddingEnd(),
            contentView.getPaddingBottom());
      } else {
        contentView.setPadding(
            paddingStart,
            contentView.getPaddingTop(),
            contentView.getPaddingRight(),
            contentView.getPaddingBottom());
      }
    }
  }

  @Override
  protected View onInflateTemplate(LayoutInflater inflater, @LayoutRes int template) {
    if (template == 0) {
      template = R.layout.sud_glif_template;
      // if the activity is embedded should apply an embedded layout.
      if (isEmbeddedActivityOnePaneEnabled(getContext())) {
        if (isGlifExpressiveEnabled()) {
          template = R.layout.sud_glif_expressive_embedded_template;
        } else {
          template = R.layout.sud_glif_embedded_template;
        }
        // TODO add unit test for this case.
      } else if (isGlifExpressiveEnabled()) {
        template = R.layout.sud_glif_expressive_template;
      } else if (ForceTwoPaneHelper.isForceTwoPaneEnable(getContext())) {
        template = R.layout.sud_glif_template_two_pane;
      }
    }
    return inflateTemplate(inflater, R.style.SudThemeGlif_Light, template);
  }

  @Override
  protected ViewGroup findContainer(int containerId) {
    if (containerId == 0) {
      containerId = R.id.sud_layout_content;
    }
    return super.findContainer(containerId);
  }

  @Override
  protected void onAttachedToWindow() {
    super.onAttachedToWindow();
    FloatingSetupProgressIndicatorMixin floatingSetupProgressIndicatorMixin =
        getMixin(FloatingSetupProgressIndicatorMixin.class);
    if (floatingSetupProgressIndicatorMixin != null) {
      floatingSetupProgressIndicatorMixin.onAttachedToWindow();
    }
    if (isGlifExpressiveEnabled()) {
      FooterBarMixin footerBarMixin = getMixin(FooterBarMixin.class);
      if (footerBarMixin != null) {
        // Ensure the footer bar guard is set up.
        footerBarMixin.ensureFooterBarGuard();
      }
    }
  }

  @Override
  protected void onDetachedFromWindow() {
    super.onDetachedFromWindow();
    // Log metrics of UI component
    if (VERSION.SDK_INT >= Build.VERSION_CODES.Q
        && WizardManagerHelper.isAnySetupWizard(activity.getIntent())
        && PartnerConfigHelper.isGlifExpressiveEnabled(getContext())) {
      FloatingBackButtonMixin floatingBackButtonMixin = getMixin(FloatingBackButtonMixin.class);
      PersistableBundle backButtonMetrics =
          floatingBackButtonMixin != null
              ? floatingBackButtonMixin.getMetrics()
              : PersistableBundle.EMPTY;
      CustomEvent customEvent =
          CustomEvent.create(MetricKey.get("SetupDesignMetrics", activity), backButtonMetrics);
      SetupMetricsLogger.logCustomEvent(getContext(), customEvent);
      LOG.atVerbose("SetupDesignMetrics=" + CustomEvent.toBundle(customEvent));
    }
    ScrollView scrollView = getScrollView();
    if (scrollView != null) {
      scrollView.getViewTreeObserver().removeOnScrollChangedListener(onScrollChangedListener);
      scrollView.getViewTreeObserver().removeOnGlobalLayoutListener(onGlobalLayoutListener);
    }
    ScrollView headerScrollView = getHeaderScrollView();
    if (headerScrollView != null) {
      headerScrollView.getViewTreeObserver().removeOnScrollChangedListener(onScrollChangedListener);
      headerScrollView.getViewTreeObserver().removeOnGlobalLayoutListener(onGlobalLayoutListener);
    }
    FloatingSetupProgressIndicatorMixin floatingSetupProgressIndicatorMixin =
        getMixin(FloatingSetupProgressIndicatorMixin.class);
    if (floatingSetupProgressIndicatorMixin != null) {
      floatingSetupProgressIndicatorMixin.onDetachFromWindow();
    }

    FooterBarMixin footerBarMixin = getMixin(FooterBarMixin.class);
    if (footerBarMixin != null && footerBarMixin.getButtonContainer() != null) {
      View buttonContainer = footerBarMixin.getButtonContainer();
      if (buttonContainer instanceof ButtonBarLayout buttonBarLayout) {
        buttonBarLayout.setOnVisibilityChangeListener(null);
      }
    }
  }

  /**
   * Sets the sticky header (i.e. header that doesn't scroll) of the layout, which is at the top of
   * the content area outside of the scrolling container. The header can only be inflated once per
   * instance of this layout.
   *
   * @param header The layout to be inflated as the header
   * @return The root of the inflated header view
   */
  public View inflateStickyHeader(@LayoutRes int header) {
    ViewStub stickyHeaderStub = findManagedViewById(R.id.sud_layout_sticky_header);
    stickyHeaderStub.setLayoutResource(header);
    return stickyHeaderStub.inflate();
  }

  /** Returns the scroll view of the header. */
  @Nullable
  public ScrollView getHeaderScrollView() {
    final View view = findManagedViewById(R.id.sud_header_scroll_view);
    return view instanceof ScrollView scrollView ? scrollView : null;
  }

  /**
   * Returns the scroll view of the layout. In the two pane mode, the view is the content area.
   * Otherwsie, it's the whole layout.
   */
  public ScrollView getScrollView() {
    final View view = findManagedViewById(R.id.sud_scroll_view);
    return view instanceof ScrollView scrollView ? scrollView : null;
  }

  public TextView getHeaderTextView() {
    return getMixin(HeaderMixin.class).getTextView();
  }

  public void setHeaderText(int title) {
    getMixin(HeaderMixin.class).setText(title);
  }

  public void setHeaderText(CharSequence title) {
    getMixin(HeaderMixin.class).setText(title);
  }

  public CharSequence getHeaderText() {
    return getMixin(HeaderMixin.class).getText();
  }

  public TextView getDescriptionTextView() {
    return getMixin(DescriptionMixin.class).getTextView();
  }

  /**
   * Sets the description text and also sets the text visibility to visible. This can also be set
   * via the XML attribute {@code app:sudDescriptionText}.
   *
   * @param title The resource ID of the text to be set as description
   */
  public void setDescriptionText(@StringRes int title) {
    getMixin(DescriptionMixin.class).setText(title);
  }

  /**
   * Sets the description text and also sets the text visibility to visible. This can also be set
   * via the XML attribute {@code app:sudDescriptionText}.
   *
   * @param title The text to be set as description
   */
  public void setDescriptionText(CharSequence title) {
    getMixin(DescriptionMixin.class).setText(title);
  }

  /** Returns the current description text. */
  public CharSequence getDescriptionText() {
    return getMixin(DescriptionMixin.class).getText();
  }

  public void setHeaderColor(ColorStateList color) {
    getMixin(HeaderMixin.class).setTextColor(color);
  }

  public ColorStateList getHeaderColor() {
    return getMixin(HeaderMixin.class).getTextColor();
  }

  public void setIcon(Drawable icon) {
    getMixin(IconMixin.class).setIcon(icon);
  }

  public void setIconVisible(boolean visible) {
    getMixin(IconMixin.class).setVisibility(visible ? View.VISIBLE : View.INVISIBLE);
  }

  public Drawable getIcon() {
    return getMixin(IconMixin.class).getIcon();
  }

  /**
   * Sets the visibility of header area in landscape mode. These views includes icon, header title
   * and subtitle. It can make the content view become full screen when set false.
   */
  @TargetApi(Build.VERSION_CODES.S)
  public void setLandscapeHeaderAreaVisible(boolean visible) {
    View view = this.findManagedViewById(R.id.sud_landscape_header_area);
    if (view == null) {
      return;
    }
    if (visible) {
      view.setVisibility(View.VISIBLE);
    } else {
      view.setVisibility(View.GONE);
    }
    updateLandscapeMiddleHorizontalSpacing();
  }

  /**
   * Sets the primary color of this layout, which will be used to determine the color of the
   * progress bar and the background pattern.
   */
  public void setPrimaryColor(@NonNull ColorStateList color) {
    primaryColor = color;
    updateBackground();
    getMixin(ProgressBarMixin.class).setColor(color);
  }

  public ColorStateList getPrimaryColor() {
    return primaryColor;
  }

  /**
   * Sets the base color of the background view, which is the status bar for phones and the full-
   * screen background for tablets. If {@link #isBackgroundPatterned()} is true, the pattern will be
   * drawn with this color.
   *
   * @param color The color to use as the base color of the background. If {@code null}, {@link
   *     #getPrimaryColor()} will be used
   */
  public void setBackgroundBaseColor(@Nullable ColorStateList color) {
    backgroundBaseColor = color;
    updateBackground();
  }

  /**
   * @return The base color of the background. {@code null} indicates the background will be drawn
   *     with {@link #getPrimaryColor()}.
   */
  @Nullable
  public ColorStateList getBackgroundBaseColor() {
    return backgroundBaseColor;
  }

  /**
   * Sets whether the background should be {@link GlifPatternDrawable}. If {@code false}, the
   * background will be a solid color.
   */
  public void setBackgroundPatterned(boolean patterned) {
    backgroundPatterned = patterned;
    updateBackground();
  }

  /** Returns true if this view uses {@link GlifPatternDrawable} as background. */
  public boolean isBackgroundPatterned() {
    return backgroundPatterned;
  }

  private void updateBackground() {
    final View patternBg = findManagedViewById(R.id.suc_layout_status);
    if (patternBg != null) {
      int backgroundColor = 0;
      if (backgroundBaseColor != null) {
        backgroundColor = backgroundBaseColor.getDefaultColor();
      } else if (primaryColor != null) {
        backgroundColor = primaryColor.getDefaultColor();
      }
      Drawable background =
          backgroundPatterned
              ? new GlifPatternDrawable(backgroundColor)
              : new ColorDrawable(backgroundColor);
      getMixin(StatusBarMixin.class).setStatusBarBackground(background);
    }
  }

  public boolean isProgressBarShown() {
    return getMixin(ProgressBarMixin.class).isShown();
  }

  public void setProgressBarShown(boolean shown) {
    getMixin(ProgressBarMixin.class).setShown(shown);
  }

  public ProgressBar peekProgressBar() {
    return getMixin(ProgressBarMixin.class).peekProgressBar();
  }

  /**
   * Returns if the current layout/activity applies heavy partner customized configurations or not.
   */
  public boolean shouldApplyPartnerHeavyThemeResource() {
    return applyPartnerHeavyThemeResource
        || (shouldApplyPartnerResource()
            && PartnerConfigHelper.shouldApplyExtendedPartnerConfig(getContext()));
  }

  /** Check if the one pane layout is enabled in embedded activity */
  protected boolean isEmbeddedActivityOnePaneEnabled(Context context) {
    boolean embeddedActivityOnePaneEnabled =
        PartnerConfigHelper.isEmbeddedActivityOnePaneEnabled(context);
    boolean activityEmbedded =
        ActivityEmbeddingController.getInstance(context)
            .isActivityEmbedded(PartnerCustomizationLayout.lookupActivityFromContext(context));
    LOG.atVerbose(
        "isEmbeddedActivityOnePaneEnabled = "
            + embeddedActivityOnePaneEnabled
            + "; isActivityEmbedded = "
            + activityEmbedded);
    return embeddedActivityOnePaneEnabled && activityEmbedded;
  }

  /** Updates the background color of this layout with the partner-customizable background color. */
  private void updateContentBackgroundColorWithPartnerConfig() {
    // If full dynamic color enabled which means this activity is running outside of setup
    // flow, the colors should refer to R.style.SudFullDynamicColorThemeGlifV3.
    if (useFullDynamicColor()) {
      return;
    }
    @ColorInt
    int color =
        PartnerConfigHelper.get(getContext())
            .getColor(getContext(), PartnerConfig.CONFIG_LAYOUT_BACKGROUND_COLOR);
    this.getRootView().setBackgroundColor(color);
    // SudGlifCardContainer style is set with a background color. Update the background color of
    // IntrinsicSizeFrameLayout with the partner-customizable background color.
    final View intrinsicSizeLayout = findManagedViewById(R.id.suc_intrinsic_size_layout);
    if (intrinsicSizeLayout != null) {
      intrinsicSizeLayout.setBackgroundColor(color);
    }
  }

  @TargetApi(VERSION_CODES.JELLY_BEAN_MR1)
  protected void tryApplyPartnerCustomizationContentPaddingTopStyle(View view) {
    Context context = view.getContext();
    boolean partnerPaddingTopAvailable =
        PartnerConfigHelper.get(context)
            .isPartnerConfigAvailable(PartnerConfig.CONFIG_CONTENT_PADDING_TOP);
    if (shouldApplyPartnerResource() && partnerPaddingTopAvailable) {
      int paddingTop =
          (int)
              PartnerConfigHelper.get(context)
                  .getDimension(context, PartnerConfig.CONFIG_CONTENT_PADDING_TOP);
      if (paddingTop != view.getPaddingTop()) {
        view.setPadding(
            view.getPaddingStart(), paddingTop, view.getPaddingEnd(), view.getPaddingBottom());
      }
    }
  }

  protected void initScrollingListener() {
    ScrollView scrollView = getScrollView();
    ScrollView headerScrollView = getHeaderScrollView();

    if (scrollView != null) {
      scrollView.getViewTreeObserver().addOnScrollChangedListener(onScrollChangedListener);
      scrollView.getViewTreeObserver().addOnGlobalLayoutListener(onGlobalLayoutListener);
    }
    if (headerScrollView != null) {
      headerScrollView.getViewTreeObserver().addOnScrollChangedListener(onScrollChangedListener);
      headerScrollView.getViewTreeObserver().addOnGlobalLayoutListener(onGlobalLayoutListener);
    }

    // Add onPreDrawListener to check the scroll state after the layout is drawn to avoid the
    // onScrollChangedListener being called before the layout is drawn.
    if (scrollView != null) {
      scrollView
          .getViewTreeObserver()
          .addOnPreDrawListener(
              new ViewTreeObserver.OnPreDrawListener() {
                @Override
                public boolean onPreDraw() {
                  if (scrollView.getViewTreeObserver().isAlive()) {
                    scrollView.getViewTreeObserver().removeOnPreDrawListener(this);
                  }
                  onInitialScrollState();
                  return true;
                }
              });
    }
    if (headerScrollView != null) {
      headerScrollView
          .getViewTreeObserver()
          .addOnPreDrawListener(
              new ViewTreeObserver.OnPreDrawListener() {
                @Override
                public boolean onPreDraw() {
                  if (headerScrollView.getViewTreeObserver().isAlive()) {
                    headerScrollView.getViewTreeObserver().removeOnPreDrawListener(this);
                  }
                  onInitialScrollState();
                  return true;
                }
              });
    }
  }

  private void onInitialScrollState() {
    // Post to the main thread to ensure the layout is drawn before we check the scroll state.
    // Otherwise, the canWholeViewsScrollDown() will return the wrong result. A small delay is
    // used here to give the layout system enough time to settle, as even a double-post can
    // sometimes be too early if the content is complex.
    postDelayed(
        () -> {
          Optional<Boolean> canScroll = canWholeViewsScrollDown();
          onScrolling(!canScroll.orElse(false));
        },
        100L);
  }

  protected void onScrolling(boolean isBottom) {
    updateBackgroundColor(isBottom);
  }

  private void updateBackgroundColor(boolean isBottom) {
    FooterBarMixin footerBarMixin = getMixin(FooterBarMixin.class);
    SystemNavBarMixin systemNavBarMixin = getMixin(SystemNavBarMixin.class);
    if (footerBarMixin != null) {
      LinearLayout footerContainer = footerBarMixin.getButtonContainer();
      if (footerContainer != null) {
        int backgroundColor =
            isBottom ? getFooterBackgroundColor() : getFooterBarMoreToScrollBackgroundColor();
        footerContainer.setBackgroundColor(backgroundColor);
        if (systemNavBarMixin != null) {
          systemNavBarMixin.setSystemNavBarBackground(backgroundColor);
        }
      }
    }
  }

  /**
   * Returns the footer background color to be used when the content is scrolled to the bottom.
   * <li>Returns TRANSPARENT if partner resources are not applied.
   * <li>Returns the theme's content background color if dynamic color is enabled.
   * <li>Returns the color from {@link PartnerConfig#CONFIG_FOOTER_BAR_BG_COLOR} if dynamic color is
   *     disabled.
   */
  public int getFooterBackgroundColor() {
    if (!shouldApplyPartnerResource()) {
      LOG.atDebug("Set footer background color as transparent");
      return Color.TRANSPARENT;
    }
    if (useFullDynamicColor()) {
      LOG.atDebug("Set footer background color as content background color");
      return getContentBackgroundColorFromStyle();
    } else {
      LOG.atDebug("Set footer background color as partner config color");
      return PartnerConfigHelper.get(getContext())
          .getColor(getContext(), PartnerConfig.CONFIG_FOOTER_BAR_BG_COLOR);
    }
  }

  /**
   * Returns the footer background color to be used when there is more content to scroll (i.e. not
   * at the bottom).
   * <li>Returns the theme's footer background color if dynamic color is enabled.
   * <li>When dynamic color is disabled, returns the color from {@link
   *     PartnerConfig#CONFIG_FOOTER_BAR_MORE_TO_SCROLL_BG_COLOR}.
   * <li>If the partner-configured color is not available or is transparent (default), it falls back
   *     to the theme attribute {@code R.attr.sudFooterBackgroundColor}.
   */
  public int getFooterBarMoreToScrollBackgroundColor() {
    if (shouldApplyDynamicColor()) {
      LOG.atDebug(
          "In scrolling state, dynamic color is enabled, using theme footer background color");
      return getColorFromTheme(R.attr.sudFooterBackgroundColor);
    }

    PartnerConfigHelper partnerConfigHelper = PartnerConfigHelper.get(getContext());
    if (partnerConfigHelper.isPartnerConfigAvailable(
        PartnerConfig.CONFIG_FOOTER_BAR_MORE_TO_SCROLL_BG_COLOR)) {
      int moreToScrollColor =
          partnerConfigHelper.getColor(
              getContext(), PartnerConfig.CONFIG_FOOTER_BAR_MORE_TO_SCROLL_BG_COLOR);
      if (moreToScrollColor != Color.TRANSPARENT) {
        LOG.atDebug("In scrolling state, using partner-configured color for footer");
        return moreToScrollColor;
      }
    }
    LOG.atDebug(
        "In scrolling state, partner color is transparent or unavailable, using theme footer"
            + " background color");
    return getColorFromTheme(R.attr.sudFooterBackgroundColor);
  }

  public boolean isShortcutIconVisible() {
    ImageButton accessibilityButton = findManagedViewById(R.id.accessibility_button);
    boolean useA11yShortcut = PartnerConfigHelper.isSuwUseA11yShortcutEnabled(getContext());
    boolean useSuwModal = PartnerConfigHelper.shouldApplyModalDialog(getContext());

    return (accessibilityButton != null && useA11yShortcut && useSuwModal);
  }

  /**
   * Make button visible and register the {@link Activity#onBackPressed()} to the on click event of
   * the floating back button. It works when {@link
   * PartnerConfigHelper#isGlifExpressiveEnabled(Context)} return true.
   */
  protected void initBackButton() {
    if (PartnerConfigHelper.isGlifExpressiveEnabled(getContext())) {
      Activity activity = PartnerCustomizationLayout.lookupActivityFromContext(getContext());
      FloatingBackButtonMixin floatingBackButtonMixin = getMixin(FloatingBackButtonMixin.class);
      if (floatingBackButtonMixin != null) {
        floatingBackButtonMixin.setVisibility(VISIBLE);
        floatingBackButtonMixin.setOnClickListener(v -> activity.onBackPressed());
      } else {
        LOG.w("FloatingBackButtonMixin button is null");
      }
    } else {
      LOG.atDebug("isGlifExpressiveEnabled is false");
    }
  }

  private void initAccessibilityButton() {
    ImageButton accessibilityButton = findManagedViewById(R.id.accessibility_button);
    boolean useA11yShortcut = PartnerConfigHelper.isSuwUseA11yShortcutEnabled(getContext());
    boolean useSuwModal = PartnerConfigHelper.shouldApplyModalDialog(getContext());

    if (accessibilityButton == null || !useA11yShortcut || !useSuwModal) {
      return;
    }

    accessibilityButton.setVisibility(View.VISIBLE);
    ItemStyler.applyFocusRingDrawable(
        getContext(), accessibilityButton, ItemStyler.FocusIndicatorShape.CIRCLE, null);
    accessibilityButton.setOnClickListener(
        v -> {
          Activity activity = PartnerCustomizationLayout.lookupActivityFromContext(getContext());

          if (PartnerConfigHelper.get(getContext())
              .isPartnerConfigAvailable(PartnerConfig.CONFIG_ASSISTIVE_OPTIONS_PACKAGE_NAME)) {
            String packageName =
                PartnerConfigHelper.get(getContext())
                    .getString(getContext(), PartnerConfig.CONFIG_ASSISTIVE_OPTIONS_PACKAGE_NAME);
            String activityName =
                PartnerConfigHelper.get(getContext())
                    .getString(getContext(), PartnerConfig.CONFIG_ASSISTIVE_OPTIONS_ACTIVITY_NAME);
            Intent intent = new Intent(packageName + "." + activityName);
            intent.setPackage(packageName);
            intent.addFlags(Intent.FLAG_ACTIVITY_REORDER_TO_FRONT);

            intent.putExtra(WizardManagerHelper.EXTRA_IS_FIRST_RUN, true);
            intent.putExtra(WizardManagerHelper.EXTRA_IS_SETUP_FLOW, true);

            if (activity != null) {
              intent.putExtra(
                  WizardManagerHelper.EXTRA_THEME, ThemeHelper.getSuwDefaultTheme(activity));
              WizardManagerHelper.copyWizardManagerExtras(activity.getIntent(), intent);
              try {
                activity.startActivityForResult(intent, ACCESSIBILITY_SETTINGS_REQUEST_CODE);
              } catch (ActivityNotFoundException e) {
                LOG.e("Activity not found: " + e.getMessage());
              }
            }
          }
        });
  }

  /**
   * Gets the footer bar background color from the current theme.
   *
   * @deprecated Not typically used, as colors are derived from dynamic color or partner configs.
   */
  @Deprecated
  public int getFooterBackgroundColorFromStyle() {
    return getColorFromTheme(R.attr.sudFooterBackgroundColor);
  }

  /**
   * Gets the standard background color ({@code android.R.attr.colorBackground}) from the current
   * theme.
   */
  @VisibleForTesting(otherwise = VisibleForTesting.PACKAGE_PRIVATE)
  public int getContentBackgroundColorFromStyle() {
    return getColorFromTheme(android.R.attr.colorBackground);
  }

  private int getColorFromTheme(@AttrRes int attr) {
    TypedValue typedValue = new TypedValue();
    Theme theme = getContext().getTheme();
    theme.resolveAttribute(attr, typedValue, true);
    return typedValue.data;
  }

  // TODO: b/398407478 - Add test case for edge to edge to layout from library.
  @Override
  public WindowInsets onApplyWindowInsets(WindowInsets insets) {
    if (isGlifExpressiveEnabled()) {
      View container = findManagedViewById(R.id.sud_layout_container);
      if (container != null) {
        container.setPadding(
            insets.getSystemWindowInsetLeft(),
            container.getPaddingTop(),
            insets.getSystemWindowInsetRight(),
            container.getPaddingBottom());
      }
      FooterBarMixin footerBarMixin = getMixin(FooterBarMixin.class);
      if (footerBarMixin != null) {
        footerBarMixin.setWindowInsets(
            insets.getSystemWindowInsetLeft(), insets.getSystemWindowInsetRight());

        // Update the background color when insets are updated to prevent the background keeps
        // transparent but the bar being lifted up by additional insets, like: keyboard.
        Optional<Boolean> canWholeViewsScrollDown = canWholeViewsScrollDown();
        if (canWholeViewsScrollDown.isPresent()) {
          updateBackgroundColor(!canWholeViewsScrollDown.get());
        }
        footerBarMixin.updateFooterBarVisibilityWhenImeVisible(insets);
      }
    }
    return super.onApplyWindowInsets(insets);
  }

  private Optional<Boolean> canWholeViewsScrollDown() {
    ScrollView scrollView = getScrollView();
    ScrollView headerScrollView = getHeaderScrollView();
    if (scrollView == null && headerScrollView == null) {
      return Optional.empty();
    }

    boolean canHeaderViewScrollDown = canViewScrollDown(headerScrollView);
    boolean canViewScrollDown = canViewScrollDown(scrollView);
    return Optional.of(canHeaderViewScrollDown || canViewScrollDown);
  }

  protected boolean isGlifExpressiveEnabled() {
    return PartnerConfigHelper.isGlifExpressiveEnabled(getContext())
        && Build.VERSION.SDK_INT >= VERSION_CODES.VANILLA_ICE_CREAM;
  }
}
