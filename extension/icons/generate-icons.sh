#!/bin/bash
# Generate PNG icons from SVG placeholder
# Requires: rsvg-convert (from librsvg) or Inkscape
# Install: brew install librsvg

for size in 16 48 128; do
  rsvg-convert -w $size -h $size icon.svg -o icon${size}.png
done

echo "Icons generated: icon16.png, icon48.png, icon128.png"
