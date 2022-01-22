from unittest import TestCase


from game.star import ClusterID

n2i_parameter_list = [
        (-5, 9),
        (-4, 7),
        (-3, 5),
        (-2, 3),
        (-1, 1),
        (0, 0),
        (1, 2),
        (2, 4),
        (3, 6),
        (4, 8),
        (5, 10)]

p2c_parameter_list = [
    (0, 0, 0),
    (1, 2, 18),
    (-1, 2, 17),
    (1, -2, 11),
    (-1, -2, 10)
]

class TestClusterID(TestCase):

    def test_natural_to_integer(self):
        for parameter_pair in n2i_parameter_list:
            with self.subTest():
                n2i = ClusterID.natural_to_integer(parameter_pair[0])
                self.assertEqual(parameter_pair[1], n2i)

    def test_integer_to_natural(self):
        for parameter_pair in n2i_parameter_list:
            with self.subTest():
                i2n = ClusterID.integer_to_natural(parameter_pair[1])
                self.assertEqual(parameter_pair[0], i2n)

    def test_point_to_cluster_id(self):
        for parameter_tuple in p2c_parameter_list:
            with self.subTest():
                p2c = ClusterID(parameter_tuple[0], parameter_tuple[1]).id
                self.assertEqual(parameter_tuple[2], p2c)

    def test_cluster_id_to_point(self):
        for parameter_tuple in p2c_parameter_list:
            with self.subTest():
                c2p = ClusterID.from_id(parameter_tuple[2])
                self.assertEqual(parameter_tuple[0], c2p.x)
                self.assertEqual(parameter_tuple[1], c2p.y)
