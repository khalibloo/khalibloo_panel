khalibloo_panel
===============
DESCRIPTION
The Khalibloo Panel hosts a growing collection of tools that handle a lot of common repetitive or tedious tasks in Blender such as changing properties of multiple objects simultaneously, editing multiple meshes at once, shape key operations, modifier operations, constraints, etc. It also contains a set of tools tailored specifically to meet the needs of DAZ Genesis (and Genesis 2) users, like auto-rigify (requires the Rigify addon enabled), importing morphs (when used with the bundled DAZ Script “Khalibloo Blender Morph Exporter”), material setup, etc.
USAGE
The addon’s UI is accessed from the properties side bar of the 3D viewport. The tools are classified into 3 platforms.

General Platform:
Tools that are not specific to any single platform can be found here.
The General platform is further divided into the following tabs:

Object tab
Apply location – Applies the location of all selected objects.
Apply rotation – Applies the rotation of all selected objects.
Apply scale – Applies the scale of all selected objects.
Selectable – Makes all objects in the scene selectable.
Unselectable – Makes all selected objects unselectable.
Renderable – Makes all selected objects visible in renders.
Unrenderable – Makes all selected objects invisible in renders.
Start Multi Edit – Begin editing of all selected mesh objects as one mesh.
End Multi Edit – End the multi editing session. Separates the meshes into their individual objects. The multi edit process uses vertex groups to keep track of which vertices belong to which mesh. Any vertices not belonging to any “Khalibloo_multiedit” vertex group at the time the multi edit session is ended will be assigned to a new mesh. It is also worth mentioning that every property (modifiers, constraints, materials, animations, etc.) the original meshes had will be restored. This is possible because the original objects are not deleted, but rather hidden in layer 20 (commonly referred to as the junk layer). If the original objects had shape keys, any changes made in the multi edit session will be added as a new shape key of the original object.

Mesh tab
Copy all shape keys – All shape keys of all selected objects will be copied to the active object.

Material tab
Receive transparent – Enable “Receive Transparent Shadows” on all materials of all selected objects. This is only useful when using Blender Render.
Remove materials – Remove all material slots on all selected objects.
Enable textures – Enable all textures on all material slots of all selected objects.
Disable textures – Disable all textures on all material slots of all selected objects.

Modifier tab
Add modifier – Add the specified modifier to all selected objects.
All or Specific – This determines how the following buttons will affect the objects. When set to “All”, every modifier will be affected; when set to “Specific”, modifiers will only be affected if they match the type selected. Note: use the selector immediately above the Add modifier button to choose the type of modifiers you want to affect.
Enable real time – turn on real time display of modifiers of all selected objects.
Disable real time – turn off real time display of modifiers of all selected objects.
Enable render – enable modifiers of all selected objects during render.
Disable render – disable modifiers of all selected objects during render.
Apply – apply modifiers (in order) of all selected objects.
Delete – delete modifiers of all selected objects.

Armature tab
Rigify neck fix – fixes a rare condition where rigify’s neck is greatly enlarged.

Constraints tab
Mute – mute all constraints of all selected objects.
Unmute – unmute all constraints of all selected objects.
Delete – delete all constraints of all selected objects.
Mute bone constraints – mute all constraints of all selected bones.
Unmute bone constraints – unmute all constraints of all selected bones.
Delete bone constraints – delete all constraints of all selected bones.

DAZ Genesis Platform:
Tools that are particularly useful for working with DAZ Genesis figures.
This platform has the figure and items tabs.
Rigify – Generate a Rigify rig for the currently active genesis figure. This process relies on positions of certain bones contained in the default genesis collada armature as well as certain vertices in the mesh itself. It is recommended that you carry out this operation immediately after importing the collada file containing the genesis figure, before any parenting, mesh edits that alter mesh topology, etc.
Rigify vertex groups – Mixes and renames the default genesis vertex groups to match rigify’s bone names. This works on clothing items as well. If this is done after Rigify, the armature modifier will be added and parenting will all be setup nicely. The process is reversible.
Unrigify vertex groups – renames the previously rigified vertex groups to their original names.
Import morphs – import all .obj files from the specified folder as shape keys of the active genesis figure.
Setup materials – sets up the materials of the active genesis figure with reasonable values for most settings. If “Merge” is enabled, materials with common diffuse maps will be merged. If “Textures” is enabled, the texture slots will be setup too. The texture slots will be set up for diffuse, spec and bump maps. However, you may still need to load in the proper maps for spec and bump.

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
