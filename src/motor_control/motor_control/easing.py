import math
# ───── original easing helpers ────────────────────────────────────────────
def ease_linear(t):              return t
def ease_in_out_quad(t):         return 2*t*t if t < 0.5 else -1+(4-2*t)*t
def ease_out_elastic(t):
    if t == 0 or t == 1: return t
    p = 0.3
    return pow(2, -10*t)*math.sin((t-p/4)*(2*math.pi)/p)+1
def ease_in_out_sine(t):         return -(math.cos(math.pi*t)-1)/2
def ease_in_out_cubic(t):        return 4*t*t*t if t < .5 else (t-1)*((2*t-2)**2)+1
def ease_in_out_poly(t):
    return 16*t**5 if t < 0.5 else 1 - 16*(1-t)**5

EASING = {
    "linear": ease_linear,
    "easeInOutQuad": ease_in_out_quad,
    "easeOutElastic": ease_out_elastic,
    "easeInOutSine": ease_in_out_sine,
    "easeInOutCubic": ease_in_out_cubic,
    "easeInOutPoly": ease_in_out_poly
}