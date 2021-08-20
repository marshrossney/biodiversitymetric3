#!/bin/bash

python generate_json.py

# I just don't like some of this formatting
target=config.json

# Habitat + condition
sed -i 's/Habitat Description/habitat/g' $target
sed -i 's/Condition/condition/g' $target

# Distinctiveness
sed -i 's/Lower Distinctiveness Habitat/LDH/g' $target
sed -i 's/Distinctiveness/distinctiveness/g' $target
sed -i 's/LDH/Lower Distinctiveness Habitat/g' $target
sed -i 's/V.Low/Very Low/g' $target
sed -i 's/V.High/Very High/g' $target

# Strategic significance
sed -i 's/Strategic Significance/strategic_significance/g' $target
sed -i 's/Within area formally identified in local strategy/High/g' $target
sed -i 's/Location ecologically desirable but not in local strategy/Medium/g' $target
sed -i 's/Area\/compensation not in local strategy\/ no local strategy/Low/g' $target

# Creation/Enhancement
sed -i 's/Technical Difficulty Creation/creation_difficulty/g' $target
sed -i 's/Technical Difficulty Enhancement/enhancement_difficulty/g' $target
sed -i 's/N\/A - //g' $target # N/A - Other
sed -i 's/N\/A -//g' $target  # N/A -Agricultural
sed -i 's/30+/30/g' $target
sed -i 's/Not Possible/null/g' $target
