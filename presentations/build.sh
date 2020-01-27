# Cleanup
rm -rf build

# Building FOSDEM2020
cd fosdem2020
npm run build
cd ..

# Aggregating
mkdir build
mkdir build/fosdem2020
touch build/.nojekyll

cp fosdem2020/deck.html build/fosdem2020/index.html
cp -r fosdem2020/img build/fosdem2020/img
