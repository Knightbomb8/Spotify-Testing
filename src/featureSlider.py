from __future__ import print_function    # (at top of module)
from PyQt5.QtCore import Qt
from superqt import *
from PyQt5.QtWidgets import (
    QCheckBox,
)

ORIENTATION = Qt.Horizontal


class FeatureSlider:
    def __init__(self, parent, name, min, max, check_box_value_changed, slider_value_changed ,is_feature_slider=False):
        # generates the slider label
        check_box = QCheckBox()
        check_box.setChecked(True)
        check_box.setText(name)
        check_box.stateChanged.connect(lambda state: check_box_value_changed(name, check_box.isChecked()))
        parent.addWidget(check_box)

        # generates the slider
        slider = QLabeledRangeSlider(ORIENTATION)
        slider.setRange(min, max)
        slider.setSingleStep(int((max - min) / 100))
        slider.setValue((min, max))
        slider.valueChanged.connect(lambda e: slider_value_changed(name, e))

        # add slider to parent widget
        parent.addWidget(slider)

        # set default values
        self.slider_values = (min, max)
        self.is_enabled = True
