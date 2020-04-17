from tft import utils, image_utils


class Board:
    def __init__(self, size):
        self.__vertices = _generate_vertices(size)

    def getGold(self):
        return self.__vertices["gold"]

    def getShop(self):
        return self.__vertices["shop"]

    def getLevel(self):
        return self.__vertices["level"]

    def getStage(self):
        return self.__vertices["stage"]

    def getStageEarly(self):
        return self.__vertices["stage_early"]

    def getPlayers(self):
        return self.__vertices["players"]

    def getHealthBars1(self):
        return self.__vertices["health_bar_names_1"], self.__vertices["health_bar_values_1"]

    def getHealthBars2(self):
        return self.__vertices["health_bar_names_2"], self.__vertices["health_bar_values_2"]


def _get_screen_size_data(size):
    data = utils.open_json_file("data/screen_sizes.json")
    user_resolution = size[1]
    range = 0.1
    for resolution in data:
        value = int(resolution)
        min_res = value * (1 - range)
        max_res = value * (1 + range)
        if min_res < user_resolution < max_res:
            return data[resolution]["contents"]
    utils.exit_with_error("Unsupported screen size: {}".format(size[1]))


def _generate_vertices(size):
    size_data = _get_screen_size_data(size)
    vertices = {"gold": __create_rectangle_from_data(size_data["gold"]),
                "shop": __create_row_of_rectangles_from_data(size_data["shop"], 5),
                "level": __create_rectangle_from_data(size_data["level"]),
                "stage": __create_rectangle_from_data(size_data["stage"]),
                "stage_early": __create_rectangle_from_data(size_data["stage_early"]),
                "health_bar_names_1": __create_column_of_rectangles_from_data(
                    size_data["health_bar_names_top_to_bottom"], 8),
                "health_bar_values_1": __create_column_of_rectangles_from_data(
                    size_data["health_bar_values_top_to_bottom"], 8),
                "health_bar_names_2": __create_column_of_rectangles_from_data(
                    size_data["health_bar_names_bottom_to_top"], 8),
                "health_bar_values_2": __create_column_of_rectangles_from_data(
                    size_data["health_bar_values_bottom_to_top"], 8),
                "players": __create_grid_of_rectangles_from_data(size_data["players"], 2, 4)}
    return vertices


def __create_grid_of_rectangles_from_data(data, rows, columns):
    return __create_grid_of_rectangles(data["x"], data["y"], data["width"], data["height"], data["x_gap"],
                                       data["y_gap"], rows, columns)


def __create_column_of_rectangles_from_data(data, rows):
    return __create_column_of_rectangles(data["x"], data["y"], data["width"], data["height"], data["gap"], rows)


def __create_row_of_rectangles_from_data(data, columns):
    return __create_row_of_rectangles(data["x"], data["y"], data["width"], data["height"], data["gap"], columns)


def __create_rectangle_from_data(data):
    return __create_rectangle(data["x"], data["y"], data["width"], data["height"])


def __create_grid_of_rectangles(x_offset, y_offset, width, height, x_gap, y_gap, rows, columns):
    result = []
    for row in range(0, rows):
        for column in range(0, columns):
            ys = [0, height]
            ys = [y + (y_offset + row * (height + y_gap)) for y in ys]
            xs = [0, width]
            xs = [x + (x_offset + column * (width + x_gap)) for x in xs]
            # leftTop, rightTop, rightBottom, leftBottom
            vertices = [[xs[0], ys[0]], [xs[1], ys[0]], [xs[1], ys[1]], [xs[0], ys[1]]]
            result.append(vertices)
    return result


def __create_column_of_rectangles(x_offset, y_offset, width, height, gap, rows):
    result = []
    for row in range(0, rows):
        ys = [0, height]
        ys = [y + (y_offset + row * (height + gap)) for y in ys]
        xs = [0, width]
        xs = [x + x_offset for x in xs]
        # leftTop, rightTop, rightBottom, leftBottom
        vertices = [[xs[0], ys[0]], [xs[1], ys[0]], [xs[1], ys[1]], [xs[0], ys[1]]]
        result.append(vertices)
    return result


def __create_row_of_rectangles(x_offset, y_offset, width, height, gap, columns):
    result = []
    for column in range(0, columns):
        ys = [0, height]
        ys = [y + y_offset for y in ys]
        xs = [0, width]
        xs = [x + (x_offset + column * (width + gap)) for x in xs]
        # leftTop, rightTop, rightBottom, leftBottom
        vertices = [[xs[0], ys[0]], [xs[1], ys[0]], [xs[1], ys[1]], [xs[0], ys[1]]]
        result.append(vertices)
    return result


def __create_rectangle(x_offset, y_offset, width, height):
    y = [y_offset, y_offset + height]
    x = [x_offset, x_offset + width]
    vertices = [[x[0], y[0]], [x[1], y[0]], [x[1], y[1]], [x[0], y[1]]]
    return [vertices]


def crop_stage(img, gameBoard):
    return image_utils.crop_shape(img, gameBoard.getStage()[0], 200)

def crop_stage_early(img, gameBoard):
    return image_utils.crop_shape(img, gameBoard.getStageEarly()[0], 200)


def crop_level(img, gameBoard):
    return image_utils.crop_shape(img, gameBoard.getLevel()[0], 150)


def crop_gold(img, gameBoard):
    return image_utils.crop_shape(img, gameBoard.getGold()[0], 150)


def crop_shop(img, gameBoard):
    return image_utils.crop_shapes(img, gameBoard.getShop(), 200)


def crop_healthbar(img, gameBoard, direction):
    if direction == 0:
        names = image_utils.crop_shapes(img, gameBoard.getHealthBars1()[0], 150)
        values = image_utils.crop_shapes(img, gameBoard.getHealthBars1()[1], 150)
    else:
        names = image_utils.crop_shapes(img, gameBoard.getHealthBars2()[0], 150)
        values = image_utils.crop_shapes(img, gameBoard.getHealthBars2()[1], 150)
    return names, values


def crop_players(img, gameBoard):
    return image_utils.crop_shapes(img, gameBoard.getPlayers(), 200)
