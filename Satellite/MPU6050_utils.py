def mean_vector(segment):
    if len(segment) == 0:
        return (0.0, 0.0, 0.0)
    sx, sy, sz = 0.0, 0.0, 0.0
    for x, y, z in segment:
        sx += x
        sy += y
        sz += z
    n = len(segment)
    return (sx / n, sy / n, sz / n)

def extract_representative_points(buffer):
    n = len(buffer)
    if n < 4:
        raise ValueError("MPU6050_utils: Buffer demasiado pequeño")
    quarter = n // 4
    segments = [
        buffer[0:quarter],
        buffer[quarter:2*quarter],
        buffer[2*quarter:3*quarter],
        buffer[3*quarter:n]
    ]
    points = [mean_vector(seg) for seg in segments]
    return points

def round_points(points, decimals=5):
    rounded = []
    for x, y, z in points:
        rounded.append((
            round(x, decimals),
            round(y, decimals),
            round(z, decimals)
        ))
    return rounded
