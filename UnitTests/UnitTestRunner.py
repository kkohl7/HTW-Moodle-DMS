import unittest
loader = unittest.TestLoader()
start_dir = 'UnitTests'
suite = loader.discover(start_dir)

runner = unittest.TextTestRunner()
runner.run(suite)