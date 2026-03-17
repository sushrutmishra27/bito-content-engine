import * as esbuild from "esbuild";
import * as fs from "fs";
import * as path from "path";

const isWatch = process.argv.includes("--watch");

// Ensure dist directory exists
if (!fs.existsSync("dist")) {
  fs.mkdirSync("dist", { recursive: true });
}

// Copy content.css to dist
fs.copyFileSync("src/content.css", "dist/content.css");

const buildOptions = {
  entryPoints: [
    "src/background.ts",
    "src/content.ts",
    "src/popup/popup.ts",
  ],
  bundle: true,
  outdir: "dist",
  format: "iife",
  target: "chrome110",
  sourcemap: true,
  minify: !isWatch,
};

if (isWatch) {
  const ctx = await esbuild.context(buildOptions);
  await ctx.watch();
  console.log("Watching for changes...");
} else {
  await esbuild.build(buildOptions);
  console.log("Build complete.");
}
