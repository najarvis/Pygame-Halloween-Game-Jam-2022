import math
import random
import pygame

def sin01(val: float) -> float:
    """Returns the sine of a value mapped between 0 and 1"""
    return (1.0 + math.sin(val)) / 2.0

def random1(pos: pygame.Vector2, seed_vec=pygame.Vector2(12.9898,78.233)) -> float:
    intermediate = math.sin(pos.dot(seed_vec)) * 43758.5453123
    return divmod(intermediate, 1)[1]

def random2(pos: pygame.Vector2, seed_vec1=pygame.Vector2(127.1,311.7), seed_vec2=pygame.Vector2(269.5,183.3)) -> pygame.Vector2:
    # https://thebookofshaders.com/12/
    intermediate = pygame.Vector2(pos.dot(seed_vec1), pos.dot(seed_vec2))
    intermediate2 = pygame.Vector2(math.sin(intermediate.x), math.sin(intermediate.y)) * 43758.5453
    return vec2_components(intermediate2)[0]

def vec2_components(vec: pygame.Vector2) -> tuple[pygame.Vector2, pygame.Vector2]:
    """Return the integer and fractional components of a vector separately"""
    x_components = divmod(vec.x, 1)
    y_components = divmod(vec.y, 1)
    f_st = pygame.Vector2(x_components[1], y_components[1])
    i_st = pygame.Vector2(x_components[0], y_components[0])
    return (f_st, i_st)

def lerp(a, b, t):
    """Linear interpolation"""
    return a * (1.0 - t) + b * t

def lerp2D(vec_a, vec_b, t):
    return pygame.Vector2(lerp(vec_a.x, vec_b.x, t), lerp(vec_a.y, vec_b.y, t))

def quintic_interpolation(a, b, t):
    new_t_curve = t * t * t * (t * (t * 6.0 - 15.0) + 10.0)
    return lerp(a, b, new_t_curve)

def smooth_noise(position: pygame.Vector2, interpolation_method=quintic_interpolation, seed_vec=pygame.Vector2(12.9898,78.233)) -> float:
    """Given a position, interpolate the random values between the corners. 
    Allows you to pass in a different interpolation function to speed up the result
    """

    # Split the position into the fractional and integer coordinates
    f_st, i_st = vec2_components(position)

    # Get the noise value at the 4 coordinates surrounding the position
    topleft     = random1(i_st, seed_vec)
    topright    = random1(i_st + pygame.Vector2(1.0, 0.0), seed_vec)
    bottomleft  = random1(i_st + pygame.Vector2(0.0, 1.0), seed_vec)
    bottomright = random1(i_st + pygame.Vector2(1.0, 1.0), seed_vec)

    # Use the fractional part of the coordinate to interpolate between the corners.
    u_x = interpolation_method(0.0, 1.0, f_st.x)
    u_y = interpolation_method(0.0, 1.0, f_st.y)

    # The return line is equivalent to an optimized version of:
    f_xy1 = lerp(topleft, topright, u_x)
    f_xy2 = lerp(bottomleft, bottomright, u_x)
    f_xy = lerp(f_xy1, f_xy2, u_y)
    return f_xy

    # return lerp(topleft, topright, u_x) + (bottomleft - topleft) * u_y * (1.0 - u_x) + (bottomright - topright) * u_x * u_y

def fBm_noise(position: pygame.Vector2, octaves: int, amplitude: float = 0.5, frequency: float = 1.0, lacunarity: float = 2.0, gain: float = 0.5, **smooth_noise_kwargs) -> float:
    """Fractal brownian motion noise. Add octaves of noise to create"""
    value = 0
    for _ in range(octaves):
        value += amplitude * smooth_noise(position * frequency, **smooth_noise_kwargs)
        frequency *= lacunarity
        amplitude *= gain

    return value

def fBm_texture(size=(256, 256), octaves=5, **kwargs):
    surf = pygame.Surface(size)
    surf.lock()
    for x in range(size[0]):
        for y in range(size[1]):
            normalized_coords = pygame.Vector2(x / size[0], y / size[1])
            val = fBm_noise(normalized_coords, octaves, **kwargs)
            # dist = 0.5
            # x_offset = math.cos(pval) * dist
            # y_offset = math.sin(pval) * dist
            # val = fBm_noise(normalized_coords + pygame.Vector2(x_offset, y_offset), octaves, **kwargs)
            col = min(255, int(val * 255))
            surf.set_at((x, y), (col, col, col))

    surf.unlock()
    return surf

def worley_noise(position: pygame.Vector2, rows: int = 4, cols: int = 4, seed_vec1=pygame.Vector2(127.1,311.7), seed_vec2=pygame.Vector2(269.5,183.3)) -> list:
    """Based on the implementation in https://thebookofshaders.com/12/, 
    retreives the distances to the points in the 9 surrounding cells. Not a
    perfect implementation because it is possible for a coordinate on the
    edge of a cell to be closer to a point two cells away.
    
    position should be a pygame.Vector2 with the x and y coordinates normalized
    between 0 and 1. Note the vector itself should not be normalized.
    
    """

    dists = []

    normalized_coords = position
    normalized_coords.x *= cols # The x coord should be in the range [0, 4] if there are 4 columns 
    normalized_coords.y *= rows

    # fractional and integer vector components of the coordinate. The integer
    # coordinate tells us which cell we are in, and the fractional coordinate
    # tells us where we are in that cell. 
    f_st, i_st = vec2_components(normalized_coords)

    # Only look at the surrounding cells
    for cell_x in range(-1, 2):
        for cell_y in range(-1, 2):
            neighbor = pygame.Vector2(cell_x, cell_y)

            # random2 is used to represent the feature point in a given cell
            r_point = random2(i_st + neighbor, seed_vec1, seed_vec2)

            diff = neighbor + r_point - f_st
            dist = diff.magnitude_squared() # Magnitude squared for speed up
            dists.append(dist)
    
    # Sort in order of increasing distance
    dists.sort()
    return dists

def worley_noise_val(dists: list[float], coefficients: list[float]):
    """Since Worley noise returns the distances to the 9 surrounding points,
    a value calculated from it is typically in the form:

    sum(Dn * Cn)
    
    coefficients does not have a set size, as the function will combine
    distances and coefficients based on whichever has fewer members.
    """
    v = 0
    for Dn, Cn in zip(dists, coefficients):
        v += Dn * Cn
    return v

def worley_texture(size=(256, 256), rows=16, cols=16, seed_vec1=pygame.Vector2(127.1,311.7), seed_vec2=pygame.Vector2(269.5,183.3)):
    surf = pygame.Surface(size)
    surf.lock()
    for x in range(size[0]):
        for y in range(size[1]):
            normalized_coords = pygame.Vector2(x / size[0] - 0.5, y / size[1] - 0.5) * 8.0
            dists = worley_noise(normalized_coords, rows, cols, seed_vec1, seed_vec2)

            v = dists[1] - dists[0]
            col = min(255, int(v * 255))
            surf.set_at((x, y), (col, col, col))

    surf.unlock()
    return surf

def random_worley_texture(size=(256, 256), rows=4, cols=4):
    worley_vec1 = pygame.Vector2(random.uniform(-1000, 1000), random.uniform(-1000, 1000))
    worley_vec2 = pygame.Vector2(random.uniform(-1000, 1000), random.uniform(-1000, 1000))
    return worley_texture(size, rows, cols, worley_vec1, worley_vec2)