import unittest

from server import compile_manifest, context_bundle


SOURCES = [
    {'name': '.cursorrules', 'content': 'Use pnpm for package operations.\nRun pnpm test before handoff.\nNever commit secrets.'},
    {'name': 'CLAUDE.md', 'content': 'Install packages with npm only.\nFollow conventional commits.'},
]


class CompilerTests(unittest.TestCase):
    def test_detects_conflict_and_applies_resolution(self):
        result = compile_manifest(SOURCES, {'packageManager': 'npm'})
        self.assertEqual(result['conflicts'][0]['key'], 'packageManager')
        self.assertIn('Use npm for all package operations.', result['manifest'])

    def test_context_bundle_is_smaller_than_manifest(self):
        compiled = compile_manifest(SOURCES)
        bundle = context_bundle(compiled['manifest'], 'review')
        self.assertLess(bundle['tokens'], compiled['outputTokens'])
        self.assertIn('Delivery', bundle['bundle'])


if __name__ == '__main__':
    unittest.main()
