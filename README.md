khalibloo_panel
===============
DESCRIPTION
The Khalibloo Panel hosts a growing collection of tools that handle a lot of common repetitive or tedious tasks in Blender such as changing properties of multiple objects simultaneously, editing multiple meshes at once, shape key operations, modifier operations, constraints, etc. It also contains a set of tools tailored specifically to meet the needs of DAZ Genesis (and Genesis 2) users, like auto-rigify (requires the Rigify addon enabled), importing morphs (when used with the bundled DAZ Script “Khalibloo Blender Morph Exporter”), material setup, etc.
USAGE
The addon’s UI is accessed from the properties side bar of the 3D viewport. The tools are classified into 3 platforms.

General Platform:
Tools that are not specific to any single platform can be found here.
The General platform is further divided into the following tabs:

DAZ Genesis Platform:
Tools that are particularly useful for working with DAZ Genesis figures.
This platform has the figure and items tabs.

DAZ Genesis 2 Platform:
Tools that are particularly useful for working with DAZ Genesis 2 figures.
The tools in this platform are identical to those in the DAZ Genesis platform except that the Rigify operation is modified slightly to fit the needs of Genesis 2 figures. And it has separate tabs for male and female figures.


DAZ GENESIS SETUP TUTORIAL
1. Export your Genesis (or Genesis 2) character from DAZ studio using collada. Recommended: enable “Merge materials by diffuse map”.
2. Import the collada file into blender. Under the Khalibloo Panel, select Genesis (or Genesis 2, depending on which one your character is) as your platform type. If your character is a Genesis 2 figure, you’ll further need to specify whether it’s the male or female figure.
3. With the character selected, click Rigify. With the character still selected, click Rigify vertex groups.
4. Now, select all your clothing items and click Rigify vertex groups.
5. For the material setup, select your character again and click Material setup. If you want spec and bump texture slots setup, enable “Texture” before clicking Material setup.

DAZ GENESIS MORPH IMPORT TUTORIAL
1. In DAZ studio, run the DAZ script “ListAllProperties” in the Script IDE tab. The results will be printed to the console below the text editor. Copy and paste the result to a new txt file (eg. in notepad). Delete any unnecessary items in the file (eg. JCMs, MCMs, Translations, etc).
2. This is hard work, i know. but once you've done it, you'll never have to do it again unless of course you install new content.
Once the text file has been created, select the character you wish to export and execute the khalibloo_blender_morph_exporter. You will see a dialog asking you to locate the text file. After that, another dialog will ask you where you want the objs to be exported. It is highly recommended that you choose an empty folder! After that, just fold your arms and sit back. It’s also worth a mention that this process works for clothes and props too.
3. Now go back into Blender and select your character (or cloth/prop, depending on which you’re working on). Above the Load morphs button, type the path to your obj folder that was created earlier. Do not use a relative path if the folder is located on a different drive/partition. Finally, click the Load morphs button. All the objs will be imported as shape keys of the active object.
