import torch
import matplotlib.pyplot as plt
import math


def softplus01_old(x, c):
    min_v = math.log(1 + math.exp(0 * 12.0 - c)) / (12 - c)
    max_v = math.log(1 + math.exp(1 * 12.0 - c)) / (12 - c)
    v = torch.log(1. + torch.exp(x * 12.0 - c)) / (12 - c)
    return (v - min_v) / (max_v - min_v)


def softplus01(x, bias, scale):
    min_v = math.log(1 + math.exp((0 - bias) * scale))
    max_v = math.log(1 + math.exp((1 - bias) * scale))
    v = torch.log(1. + torch.exp((x - bias) * scale))
    return (v - min_v) / (max_v - min_v)


def inv_softplus01(x, bias, scale):
    min_v = ((torch.zeros(1, dtype=x.dtype, device=x.device) - bias) * scale).expm1().clamp(min=1e-6).log()
    max_v = ((torch.ones(1, dtype=x.dtype, device=x.device) - bias) * scale).expm1().clamp(min=1e-6).log()
    v = ((x - bias) * scale).expm1().clamp(min=1e-6).log()
    return (v - min_v) / (max_v - min_v)


def hardplus(x, scale):
    threshold = (1.0 - (1.0 / scale))
    index = threshold <= x
    y = torch.zeros_like(x)
    y[index] = (x[index] - threshold) * scale
    return y


def distance_to_disparity(x, c):
    c1 = 1.0 + c
    min_v = c / c1
    return ((c / (c1 - x)) - min_v) / (1.0 - min_v)


def inv_distance_to_disparity(x, c):
    # y = ((c / ((1.0 + c) - x)) - (c / (1.0 + c))) / (1.0 - (c / (1.0 + c)))
    # x = ((c + 1) * y) / (y + c)
    return ((c + 1) * x) / (x + c)


def shift_relative_depth(x, min_distance, max_distance=16):
    # convert x from dispariy space to distance space
    # reference: https://github.com/LiheYoung/Depth-Anything/issues/72#issuecomment-1937892879
    provisional_max_distance = min_distance + max_distance
    A = 1.0 / provisional_max_distance
    B = (1.0 / min_distance) - (1.0 / provisional_max_distance)
    distance = 1 / (A + B * x)

    # shift distance in distance space. old min_distance -> 1
    new_min_distance = 1.0
    distance = (new_min_distance - min_distance) + distance

    # back to disparity space
    new_x = 1.0 / distance

    # scale output to 0-1 range
    # NOTE: Do not use new_x.amin()/new_x.amax() to avoid re-normalization.
    #       This condition is required when using EMA normalization with look-ahead buffers.
    min_value = 1.0 / (max_distance + 1)
    value_range = 1.0 - 1.0 / (max_distance + 1)
    new_x = (new_x - min_value) / value_range

    return new_x


def find_softplus_v2_main():
    def find_softplus_v1_to_v2(c):
        # c=4, bias=0.333, scale=12
        # c=6, bias=0.5, scale=12
        # c=8.4, bias=0687, scale=12

        x = torch.linspace(0, 1, 1000)
        y = softplus01_old(x, c)
        best_score = 10000000
        hist = []
        for bias in torch.linspace(0, 1, 100).tolist():
            for scale in torch.linspace(0, 20, 100).tolist():
                y2 = softplus01(x, bias=bias, scale=scale)
                score = (y - y2).abs().mean().item()
                if best_score > score:
                    best_score = score
                    hist.append((score, dict(c=c, bias=bias, scale=scale)))

        print(f"** c={c} top 10:")
        for score, param in hist[-10:]:
            print("MAE", round(score, 5), "bias", round(param["bias"], 3), "scale", round(param["scale"], 3))

    # c=4, bias=0.333, scale=12
    # c=6, bias=0.5, scale=12
    # c=8.4, bias=0.687, scale=12
    find_softplus_v1_to_v2(4)
    find_softplus_v1_to_v2(6)
    find_softplus_v1_to_v2(8.4)


def find_softplus_mul_main():
    def find_softplus(mul_scale, margin=0.2):
        threshold = (1.0 - (1.0 / mul_scale))
        threshold += threshold * margin
        x = torch.linspace(threshold, 1, 1000)
        y = hardplus(x, mul_scale)

        best_score = 10000000
        hist = []
        for bias in torch.linspace(0, 1, 100).tolist():
            # for scale in torch.linspace(0, 20, 100).tolist():
            scale = 12
            y2 = softplus01(x, bias=bias, scale=scale)
            score = (y - y2).abs().mean().item()
            if best_score > score:
                best_score = score
                hist.append((score, dict(bias=bias, scale=scale)))

        print(f"** mul_scale={mul_scale} top 10:")
        for score, param in hist[-10:]:
            print("MAE", round(score, 5), "bias", round(param["bias"], 3), "scale", round(param["scale"], 3))

    find_softplus(1.5)
    find_softplus(2)
    find_softplus(3)


def check_find_softplus_mul_main():
    # result: https://github.com/nagadomi/nunif/assets/287255/2be5c0de-cb72-4c9c-9e95-4855c0730e5c
    x = torch.linspace(0, 1, 1000)

    plt.plot(x, x, label="none")

    y = hardplus(x, 1.5)
    y2 = softplus01(x, bias=0.343, scale=12)
    plt.plot(x, y, label="hard_mul_1.5")
    plt.plot(x, y2, label="soft_mul_1.5")

    y = hardplus(x, 2)
    y2 = softplus01(x, bias=0.515, scale=12)
    plt.plot(x, y, label="hard_mul_2")
    plt.plot(x, y2, label="soft_mul_2")

    y = hardplus(x, 3)
    y2 = softplus01(x, bias=0.687, scale=12)
    plt.plot(x, y, label="hard_mul_3")
    plt.plot(x, y2, label="soft_mul_3")

    plt.legend()
    plt.show()


def find_inv_softplus_main():
    def find_inv_softplus(softplus_bias, softplus_scale, mul_scale, margin=0.2):
        threshold = (1.0 - (1.0 / mul_scale))
        threshold += threshold * margin
        error_scale2 = (1.0 - threshold) / threshold
        x = torch.linspace(0, 1, 1000)
        y = softplus01(x, softplus_bias, softplus_scale)
        index1 = x <= threshold
        index2 = torch.logical_not(x <= threshold)
        best_score = 10000000
        hist = []
        # NOTE: inv_softplus is sensitive to very small difference of bias
        for bias in torch.linspace(-0.1, 0.1, 1000).tolist():
            for scale in torch.linspace(-20, 20, 100).tolist():
                # y = f(x)
                # x2 = inv_f(y)
                # minimize (x - x2)**2
                x2 = inv_softplus01(y, bias=bias, scale=scale)
                error1 = (x[index1] - x2[index1]).pow(2).mean().item()
                error2 = (x[index2] - x2[index2]).pow(2).mean().item()
                score = error1 + error2 * error_scale2
                if best_score > score:
                    best_score = score
                    hist.append((score, dict(bias=bias, scale=scale)))

        print(f"** bias={softplus_bias},scale={softplus_scale} top 10:")
        for score, param in hist[-10:]:
            print("MSE", round(score, 5), "bias", round(param["bias"], 6), "scale", round(param["scale"], 4))

    find_inv_softplus(softplus_bias=0.343, softplus_scale=12, mul_scale=1.5)
    find_inv_softplus(softplus_bias=0.515, softplus_scale=12, mul_scale=2)
    find_inv_softplus(softplus_bias=0.687, softplus_scale=12, mul_scale=3)


def check_find_inv_softplus_main():
    # result: https://github.com/nagadomi/nunif/assets/287255/f580b405-b0bf-4c6a-8362-66372b2ed930
    x = torch.linspace(0, 1, 1000)
    plt.plot(x, x, label="none")

    y = softplus01(x, bias=0.343, scale=12)
    y2 = inv_softplus01(x, bias=-0.002102, scale=7.8788)
    plt.plot(x, y, label="soft_mul_1.5")
    plt.plot(x, y2, label="soft_mul_1.5_inv")

    y = softplus01(x, bias=0.515, scale=12)
    y2 = inv_softplus01(x, bias=-0.0003, scale=6.2626)
    plt.plot(x, y, label="soft_mul_2")
    plt.plot(x, y2, label="soft_mul_2_inv")

    y = softplus01(x, bias=0.687, scale=12)
    y2 = inv_softplus01(x, bias=-0.0001, scale=3.4343)
    plt.plot(x, y, label="soft_mul_3")
    plt.plot(x, y2, label="soft_mul_3_inv")

    plt.legend()
    plt.show()


def _check_inv_distance_to_disparity_main():
    # NOT USED
    # Should use larger `c` distance_to_disparity
    x = torch.linspace(0, 1, 1000)
    plt.plot(x, x, label="none")

    y = distance_to_disparity(x, 0.6)
    y2 = inv_distance_to_disparity(x, 0.6)
    plt.plot(x, y, label="disparity_0.6")
    plt.plot(x, y2, label="inv_distance_0.6")

    y = distance_to_disparity(x, 0.4)
    y2 = inv_distance_to_disparity(x, 0.4)
    plt.plot(x, y, label="disparity_0.4")
    plt.plot(x, y2, label="inv_distance_0.4")

    y = distance_to_disparity(x, 0.2)
    y2 = inv_distance_to_disparity(x, 0.2)
    plt.plot(x, y, label="disparity_0.2")
    plt.plot(x, y2, label="inv_distance_0.2")

    y = distance_to_disparity(x, 0.1)
    y2 = inv_distance_to_disparity(x, 0.1)
    plt.plot(x, y, label="disparity_0.1")
    plt.plot(x, y2, label="inv_distance_0.1")

    plt.legend()
    plt.show()


def check_distance_to_disparity_main():
    # result: https://github.com/nagadomi/nunif/assets/287255/46c6b292-040f-4820-93fc-9e001cd53375
    x = torch.linspace(0, 1, 1000)
    plt.plot(x, x, label="none")

    for c in (2.5, 1, 0.6, 0.4, 0.2, 0.1):
        y = distance_to_disparity(x, c)
        plt.plot(x, y, label=f"{c}")

    plt.legend()
    plt.show()


def check_shift_relative_depth_main():
    # result: https://github.com/user-attachments/assets/7c953aae-101e-4337-82b4-10a073863d47
    x = torch.linspace(0, 1, 1000)
    plt.plot(x, x, label="none")

    for c in (1.4, 2, 3.0, 0.8, 0.6, 0.45):
        y = shift_relative_depth(x, c)
        plt.plot(x, y, label=f"{c}")

    plt.legend()
    plt.show()


if __name__ == "__main__":
    # find_softplus_v2_main()
    # find_softplus_mul_main()
    # check_find_softplus_mul_main()
    # find_inv_softplus_main()
    # check_find_inv_softplus_main()
    #check_distance_to_disparity_main()
    check_shift_relative_depth_main()
