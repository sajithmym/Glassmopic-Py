"""Reusable animation helpers for Glassmopic widgets."""

from PyQt5.QtCore import (
    QPropertyAnimation, QEasingCurve, QParallelAnimationGroup,
    QSequentialAnimationGroup, QAbstractAnimation, QObject, pyqtProperty, Qt
)
from PyQt5.QtWidgets import QWidget, QGraphicsOpacityEffect, QGraphicsDropShadowEffect
from PyQt5.QtGui import QColor


def fade_in(widget: QWidget, duration: int = 350, start: float = 0.0,
            end: float = 1.0, curve: QEasingCurve.Type = QEasingCurve.OutCubic) -> QPropertyAnimation:
    """Fade a widget from `start` to `end` opacity."""
    effect = QGraphicsOpacityEffect(widget)
    widget.setGraphicsEffect(effect)
    anim = QPropertyAnimation(effect, b"opacity", widget)
    anim.setDuration(duration)
    anim.setStartValue(start)
    anim.setEndValue(end)
    anim.setEasingCurve(curve)
    anim.start(QAbstractAnimation.DeleteWhenStopped)
    return anim


def slide_fade_in(widget: QWidget, duration: int = 400,
                  offset: int = 30) -> QParallelAnimationGroup:
    """Slide up + fade in simultaneously."""
    group = QParallelAnimationGroup(widget)

    # Opacity
    opacity_effect = QGraphicsOpacityEffect(widget)
    widget.setGraphicsEffect(opacity_effect)
    fade = QPropertyAnimation(opacity_effect, b"opacity", widget)
    fade.setDuration(duration)
    fade.setStartValue(0.0)
    fade.setEndValue(1.0)
    fade.setEasingCurve(QEasingCurve.OutCubic)
    group.addAnimation(fade)

    # Position shift (use maximumHeight trick via geometry)
    pos_anim = QPropertyAnimation(widget, b"pos", widget)
    start_pos = widget.pos()
    pos_anim.setDuration(duration)
    from PyQt5.QtCore import QPoint
    pos_anim.setStartValue(QPoint(start_pos.x(), start_pos.y() + offset))
    pos_anim.setEndValue(start_pos)
    pos_anim.setEasingCurve(QEasingCurve.OutCubic)
    group.addAnimation(pos_anim)

    group.start(QAbstractAnimation.DeleteWhenStopped)
    return group


class ShadowAnimator(QObject):
    """Animates shadow blur radius for hover elevation effect."""

    def __init__(self, shadow_effect: QGraphicsDropShadowEffect, parent=None):
        super().__init__(parent)
        self._shadow = shadow_effect
        self._blur = shadow_effect.blurRadius()

    @pyqtProperty(float)
    def blur(self) -> float:
        return self._blur

    @blur.setter
    def blur(self, value: float) -> None:
        self._blur = value
        self._shadow.setBlurRadius(value)

    @pyqtProperty(float)
    def offsetY(self) -> float:
        return self._shadow.offset().y()

    @offsetY.setter
    def offsetY(self, value: float) -> None:
        self._shadow.setOffset(self._shadow.offset().x(), value)


def animate_shadow(animator: ShadowAnimator, target_blur: float,
                   target_y: float, duration: int = 200) -> QParallelAnimationGroup:
    """Smoothly animate shadow blur + offset."""
    group = QParallelAnimationGroup(animator)

    blur_anim = QPropertyAnimation(animator, b"blur", animator)
    blur_anim.setDuration(duration)
    blur_anim.setEndValue(target_blur)
    blur_anim.setEasingCurve(QEasingCurve.OutCubic)
    group.addAnimation(blur_anim)

    y_anim = QPropertyAnimation(animator, b"offsetY", animator)
    y_anim.setDuration(duration)
    y_anim.setEndValue(target_y)
    y_anim.setEasingCurve(QEasingCurve.OutCubic)
    group.addAnimation(y_anim)

    group.start(QAbstractAnimation.DeleteWhenStopped)
    return group


def staggered_fade_in(widgets: list, base_delay: int = 50,
                      duration: int = 350) -> QSequentialAnimationGroup:
    """Fade in a list of widgets with staggered delay."""
    group = QSequentialAnimationGroup()
    for i, w in enumerate(widgets):
        effect = QGraphicsOpacityEffect(w)
        w.setGraphicsEffect(effect)
        effect.setOpacity(0.0)
        anim = QPropertyAnimation(effect, b"opacity", w)
        anim.setDuration(duration)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.OutCubic)
        if i > 0:
            group.addPause(base_delay)
        group.addAnimation(anim)
    group.start(QAbstractAnimation.DeleteWhenStopped)
    return group
