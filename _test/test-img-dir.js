import {BrewTester} from "5etools-utils";

const _ALLOWLIST_DIRS = new Set([
	"dkNinja",
]);

await BrewTester.pTestImgDirectories({
	dirAllowlist: _ALLOWLIST_DIRS,
});
