# Cleanup
rm -rf build

# Building FOSDEM2020
cd fosdem2020
npm run build
cd ..

# Aggregating
FOSDEM2020=build/presentations/fosdem2020
mkdir -p $FOSDEM2020
touch build/.nojekyll

cp fosdem2020/deck.html $FOSDEM2020/index.html
cp -r fosdem2020/img $FOSDEM2020/img
