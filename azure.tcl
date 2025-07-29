# Azure-ttk-theme - v2.1.0 (Corrected)
# https://github.com/rdbende/Azure-ttk-theme

package require Tk 8.6

namespace eval ttk::theme::azure {
    variable colors
    array set colors {
        # Light theme
        light-bg          "#ffffff"
        light-fg          "#000000"
        light-border      "#adadad"
        light-accent      "#0078d4"
        light-accent-fg   "#ffffff"
        light-select-bg   "#0078d4"
        light-select-fg   "#ffffff"
        light-disabled-fg "#8d8d8d"
        light-disabled-bg "#f0f0f0"
        light-danger      "#e81123"

        # Dark theme
        dark-bg           "#2d2d2d"
        dark-fg           "#ffffff"
        dark-border       "#4a4a4a"
        dark-accent       "#0078d4"
        dark-accent-fg    "#ffffff"
        dark-select-bg    "#005a9e"
        dark-select-fg    "#ffffff"
        dark-disabled-fg  "#7d7d7d"
        dark-disabled-bg  "#383838"
        dark-danger       "#e81123"
    }

    proc SetColors {mode} {
        variable colors
        ttk::style configure . \
            -background $colors($mode-bg) \
            -foreground $colors($mode-fg) \
            -bordercolor $colors($mode-border) \
            -troughcolor $colors($mode-bg) \
            -selectbackground $colors($mode-select-bg) \
            -selectforeground $colors($mode-select-fg) \
            -insertcolor $colors($mode-fg) \
            -font {Segoe\ UI 10}

        ttk::style map . \
            -background [list disabled $colors($mode-disabled-bg)] \
            -foreground [list disabled $colors($mode-disabled-fg)]

        ttk::style configure TButton \
            -background $colors($mode-bg) \
            -foreground $colors($mode-fg) \
            -bordercolor $colors($mode-border) \
            -focuscolor $colors($mode-accent) \
            -padding {10 5}

        ttk::style map TButton \
            -background [list active $colors($mode-disabled-bg) pressed $colors($mode-disabled-bg)] \
            -bordercolor [list active $colors($mode-border)] \
            -relief [list pressed sunken]

        ttk::style configure Accent.TButton \
            -background $colors($mode-accent) \
            -foreground $colors($mode-accent-fg) \
            -bordercolor $colors($mode-accent)

        ttk::style map Accent.TButton \
            -background [list active $colors($mode-select-bg) pressed $colors($mode-select-bg)] \
            -bordercolor [list active $colors($mode-accent)]

        ttk::style configure Danger.TButton \
            -background $colors($mode-danger) \
            -foreground $colors($mode-accent-fg) \
            -bordercolor $colors($mode-danger)

        ttk::style map Danger.TButton \
            -background [list active #a10d18 pressed #a10d18] \
            -bordercolor [list active $colors($mode-danger)]

        ttk::style configure TEntry \
            -fieldbackground $colors($mode-bg)

        ttk::style map TEntry \
            -fieldbackground [list focus $colors($mode-bg)] \
            -bordercolor [list focus $colors($mode-accent)]

        ttk::style configure TCombobox \
            -background $colors($mode-bg) \
            -foreground $colors($mode-fg) \
            -bordercolor $colors($mode-border) \
            -arrowcolor $colors($mode-fg) \
            -focuscolor $colors($mode-accent) \
            -padding {10 5}

        ttk::style map TCombobox \
            -background [list active $colors($mode-disabled-bg) pressed $colors($mode-disabled-bg)] \
            -bordercolor [list active $colors($mode-border)] \
            -relief [list pressed sunken]

        ttk::style configure TCheckbutton \
            -background $colors($mode-bg) \
            -indicatorbackground $colors($mode-bg) \
            -indicatormargin 0 \
            -indicatordiameter 20

        ttk::style map TCheckbutton \
            -indicatorbackground [list selected $colors($mode-accent) active $colors($mode-disabled-bg)] \
            -indicatorforeground [list selected $colors($mode-accent-fg)]

        ttk::style configure TRadiobutton \
            -background $colors($mode-bg) \
            -indicatorbackground $colors($mode-bg) \
            -indicatormargin 0 \
            -indicatordiameter 20

        ttk::style map TRadiobutton \
            -indicatorbackground [list selected $colors($mode-accent) active $colors($mode-disabled-bg)] \
            -indicatorforeground [list selected $colors($mode-accent-fg)]

        ttk::style configure TMenubutton \
            -background $colors($mode-bg) \
            -padding {10 5}

        ttk::style map TMenubutton \
            -background [list active $colors($mode-disabled-bg)]

        ttk::style configure TSpinbox \
            -arrowsize 18 \
            -padding {10 5}

        ttk::style map TSpinbox \
            -background [list readonly $colors($mode-disabled-bg)]

        ttk::style configure TScale \
            -background $colors($mode-bg)

        ttk::style configure TNotebook.Tab \
            -background $colors($mode-disabled-bg) \
            -bordercolor $colors($mode-border) \
            -padding {10 5}

        ttk::style map TNotebook.Tab \
            -background [list selected $colors($mode-bg) active $colors($mode-bg)] \
            -bordercolor [list selected $colors($mode-border)]

        ttk::style configure TProgressbar \
            -background $colors($mode-accent)

        ttk::style configure TSeparator \
            -background $colors($mode-border)

        ttk::style configure Treeview \
            -fieldbackground $colors($mode-bg)

        ttk::style map Treeview \
            -background [list selected $colors($mode-select-bg)] \
            -foreground [list selected $colors($mode-select-fg)]
    }
}

ttk::style theme create azure -parent clam
ttk::style theme create azure-dark -parent azure
ttk::style theme create azure-light -parent azure