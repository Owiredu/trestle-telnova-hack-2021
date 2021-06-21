# -*- mode: python -*-

block_cipher = None


a = Analysis(['alpha_main.py',
              'add_new_stream_ui.py',
              'alpha_ui.py',
              'db_conn.py',
              'mdi_content_ui.py',
              'play_tag_sound.py',
              'video_player_main.py',
              'video_player_ui.py',
              'video_processing_thread.py',
              'vlc.py'],
             pathex=['C://Users//ROSAR//Desktop//alpha_counter'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='Alpha',
          debug=False,
          strip=False,
          upx=True,
          console=False,
	  icon='icons//alpha_icon.png')

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='Alpha',
               icon='icons//alpha_icon.png')
