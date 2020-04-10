from tft import utils


class GameBoard:
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

    def getPlayers(self):
        return self.__vertices["players"]

    def getHealthBars1(self):
        return self.__vertices["health_bar_names_1"], self.__vertices["health_bar_values_1"]

    def getHealthBars2(self):
        return self.__vertices["health_bar_names_2"], self.__vertices["health_bar_values_2"]


def _generate_vertices(size):
    data = utils.open_json_file("data/screen_sizes.json")
    if str(size[1]) not in data:
        utils.exit_with_error("Unsupported screen size: {}".format(size[1]))
    size_data = data[str(size[1])]["contents"]
    vertices = {"gold": __create_rectangle_from_data(size_data["gold"]),
                "shop": __create_row_of_rectangles_from_data(size_data["shop"], 5),
                "level": __create_rectangle_from_data(size_data["level"]),
                "stage": __create_rectangle_from_data(size_data["stage"]),
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


def __create_column_of_rectangles_from_data(data, repeat):
    return __create_column_of_rectangles(data["x"], data["y"], data["width"], data["height"], data["gap"], repeat)


def __create_row_of_rectangles_from_data(data, repeat):
    return __create_row_of_rectangles(data["x"], data["y"], data["width"], data["height"], data["gap"], repeat)


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


def __create_column_of_rectangles(x_offset, y_offset, width, height, gap, repeat):
    result = []
    for row in range(0, repeat):
        ys = [0, height]
        ys = [y + (y_offset + row * (height + gap)) for y in ys]
        xs = [0, width]
        xs = [x + x_offset for x in xs]
        # leftTop, rightTop, rightBottom, leftBottom
        vertices = [[xs[0], ys[0]], [xs[1], ys[0]], [xs[1], ys[1]], [xs[0], ys[1]]]
        result.append(vertices)
    return result


def __create_row_of_rectangles(x_offset, y_offset, width, height, gap, repeat):
    result = []
    for column in range(0, repeat):
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
