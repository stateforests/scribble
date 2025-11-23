# Scribble
Simple GUI tool for mass-submitting Color Book level runs to Speedrun.com.

### Adding Runs
1. Click **Authenticate** and use your Speedrun.com details
2. Fill in the form:
   - **Category**: Auto-selected, but can be done manually (Solo/Duo/Trio/Quartet/Squad)
   - **Map**: Map played (this automatically fetches from the API)
   - **Gear**: Gearless or Gear, based on what is used in the run
   - **Players**: Comma-separated player names (e.g. `player1,player2,player3`)
   - **Time**: Formatted as `MM:SS.mmm` or `HH:MM:SS.mmm` (I'd be concerned if your run was hours long)
   - **Video URL**: YouTube or whatever your run is uploaded to
   - **Description**: Additional POVs or notes on the run I guess
3. Click **Add Run** to add it to your queue
4. Repeat for all applicable runs
5. Click **Submit All Runs** to mass-submit

### Importing from Text File
Create a text file, one run per line, in this format:
```
player1,player2 | Map Name | 1:23.456 | Gearless | https://youtu.be/example | <Additional POVs if applicable>
```
Click **Import Text** and select your file.
