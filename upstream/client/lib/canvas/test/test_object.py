
#
# TESTS
#

from unittest import TestCase

from canvas.object import Object, ObjectSet, ErrorInvalidObject


class ObjectTestCase(TestCase):

    def setUp(self):
        pass

    def test_object_parse_empty(self):
        o1 = Object({})

        self.assertEqual(None, o1.name)
        self.assertEqual(None, o1.data)
        self.assertEqual(None, o1.xsum)
        self.assertEqual([], o1.actions)

    def test_object_parse_invalid(self):
        # checksum must match if set
        with self.assertRaises(ErrorInvalidObject):
            Object({'name': 'foo', 'checksum':{'sha256': ''}, 'actions':[] })

        with self.assertRaises(ErrorInvalidObject):
            Object({'name': 'foo', 'data': 'abc', 'checksum':{'sha256': ''}, 'actions':[] })

    def test_object_parse_dict(self):
        o1 = Object({
                'name': 'foo',
                'data': 'abc',
                'checksum':{'sha256': 'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad'},
                'actions':[]
            })

        self.assertEqual('foo', o1.name)
        self.assertEqual('abc', o1.data)
        self.assertEqual('ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad', o1.xsum)
        self.assertEqual([], o1.actions)


    def test_objectset_equality(self):
        o1 = Object({
                'name': 'foo',
                'data': 'abc',
                'checksum':{'sha256': 'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad'},
                'actions':[]
            })

        o2 = Object({
                'name': 'bar',
                'data': 'abc',
                'checksum':{'sha256': 'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad'},
                'actions':[]
            })

        o3 = Object({
                'name': 'baz',
                'data': 'xyz',
                'checksum':{'sha256': '3608bca1e44ea6c4d268eb6db02260269892c0b42b86bbf1e77a6fa16c3c9282'},
                'actions':[]
            })

        l1 = ObjectSet()
        l2 = ObjectSet()

        l1.add(o1)
        l2.add(o2)
        self.assertEqual(l1, l2)

        l1.add(o3)
        self.assertNotEqual(l1, l2)

    def test_objectset_update(self):
        o1 = Object({
                'name': 'foo',
                'data': 'abc',
                'checksum':{'sha256': 'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad'},
                'actions':[]
            })

        o2 = Object({
                'name': 'bar',
                'data': 'abc',
                'checksum':{'sha256': 'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad'},
                'actions':[]
            })

        o3 = Object({
                'name': 'baz',
                'data': 'xyz',
                'checksum':{'sha256': '3608bca1e44ea6c4d268eb6db02260269892c0b42b86bbf1e77a6fa16c3c9282'},
                'actions':[]
            })

        l1 = ObjectSet()
        l2 = ObjectSet()

        l1.add(o2)
        l1.add(o3)

        self.assertEqual(ObjectSet([o2, o3]), l1)

        l2.add(o1)
        self.assertEqual(ObjectSet([o1]), l2)

        l2.update(l1)
        self.assertEqual(ObjectSet([o2, o3]), l2)

    def test_objectset_uniqueness(self):
        o1 = Object({
                'name': 'foo',
                'data': 'abc',
                'checksum':{'sha256': 'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad'},
                'actions':[]
            })

        o2 = Object({
                'name': 'bar',
                'data': 'abc',
                'checksum':{'sha256': 'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad'},
                'actions':[]
            })

        o3 = Object({
                'name': 'baz',
                'data': 'xyz',
                'checksum':{'sha256': '3608bca1e44ea6c4d268eb6db02260269892c0b42b86bbf1e77a6fa16c3c9282'},
                'actions':[]
            })

        l1 = ObjectSet()

        l1.add(o1)
        self.assertTrue(len(l1) == 1)

        # adding second object of same checksum should overwrite
        # existing object with undefined arch
        l1.add(o2)
        self.assertTrue(len(l1) == 1)
        self.assertTrue(ObjectSet([o2]), l1)

        l1.add(o3)
        self.assertTrue(len(l1) == 2)
        self.assertTrue(ObjectSet([o2, o3]), l1)

    def test_objectset_difference(self):
        o1 = Object({
                'name': 'foo',
                'data': 'abc',
                'checksum':{'sha256': 'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad'},
                'actions':[]
            })

        o2 = Object({
                'name': 'bar',
                'data': 'abc',
                'checksum':{'sha256': 'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad'},
                'actions':[]
            })

        o3 = Object({
                'name': 'baz',
                'data': 'xyz',
                'checksum':{'sha256': '3608bca1e44ea6c4d268eb6db02260269892c0b42b86bbf1e77a6fa16c3c9282'},
                'actions':[]
            })

        l1 = ObjectSet([o1, o3])
        l2 = ObjectSet([o2])

        (luniq1, luniq2) = l1.difference(l2)

        self.assertEqual(ObjectSet([o3]), luniq1)
        self.assertEqual(ObjectSet([]), luniq2)


if __name__ == "__main__":
    import unittest
    suite = unittest.TestLoader().loadTestsFromTestCase(ObjectTestCase)
    unittest.TextTestRunner().run(suite)
