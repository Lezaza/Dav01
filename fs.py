
import os
import argparse
import uuid
import time
import hashlib
import copy

import tornado.web
import tornado.httpclient
import tornado.escape

import ecdsa

import database
import chain

folder_names = {}
def get_folders(reload=False):
    global folder_names
    pirmary = None
    if folder_names or not reload:
        folder_names = {}
        for block in chain.get_chain():
            block_data_json = block[5]
            block_data = tornado.escape.json_decode(block_data_json)
            # print(names)
            if block_data.get('type') == 'folder':
                print('get_folders block', block_data)
                # if 'name' in block_data:
                name = block_data['name']
                meta_hash = block_data.get('meta_hash', '')
                # update_time = block_data['update_time']
                # if name:
                folder_names[name] = meta_hash #[items, update_time]
    print('get_folders', folder_names)
    return folder_names

storage_names = {}
def get_storages(reload=False):
    global storage_names
    pirmary = None
    if storage_names or not reload:
        storage_names = {}
        for block in chain.get_chain():
            block_data_json = block[5]
            block_data = tornado.escape.json_decode(block_data_json)
            # print(names)
            if block_data.get('type') == 'storage':
                print('get_storages block', block_data)
                # if 'name' in block_data:
                name = block_data['name']
                path = block_data.get('path', '')
                node_name = block_data.get('node_name', '')
                # if name:
                storage_names[name] = [path, node_name]
    print('get_storages', storage_names)
    return storage_names


class TestHandler(tornado.web.RequestHandler):
    def get(self):
        self.finish('chain test')


class ListFoldersHandler(tornado.web.RequestHandler):
    def get(self):
        for folder_name in get_folders():
            self.write('<a href="/*list_files?folder_name=%s">List</a> %s<br>\n' % (folder_name, folder_name))
        self.finish('\n')

class ListFilesHandler(tornado.web.RequestHandler):
    def get(self):
        folder_name = self.get_argument('folder_name')
        folders = get_folders()
        folder_meta_hash = folders.get(folder_name, '')

        storages = get_storages()
        for storage_name, storage_payload in storages.items():
            storage_path = storage_payload[0]
            node_name = storage_payload[1]
            if node_name == chain.current_name:
                if os.path.exists('%s/meta/%s' % (storage_path, folder_meta_hash)):
                    with open('%s/meta/%s' % (storage_path, folder_meta_hash), 'rb') as f:
                        folder_meta_json = f.read()
                        folder_meta_data = tornado.escape.json_decode(folder_meta_json)
                        assert folder_meta_data['type'] == 'folder_meta'
                        break

        self.write('Node name %s storage path %s<br>\n' % (node_name, storage_path))
        self.write('%s %s<br>\n' % (folder_name, folder_meta_hash))
        for item_name, file_meta_data in folder_meta_data['items'].items():
            self.write('%s %s <br>\n' % (item_name, str(file_meta_data)))
        self.finish('\n')

class GetFolderHandler(tornado.web.RequestHandler):
    def get(self):
        folder_name = self.get_argument('folder_name')
        folders = get_folders()
        folder_meta_hash = folders.get(folder_name, '')
        self.finish({'name': folder_name, 'meta_hash': folder_meta_hash})


class AddFolderHandler(tornado.web.RequestHandler):
    def get(self):
        names = get_folders()
        self.finish('''%s<br><form method="POST">
            <input name="folder_name" placeholder="Folder" />
            <input type="submit" value="Add"/></form>\n''' % names)

    @tornado.gen.coroutine
    def post(self):
        folder_name = self.get_argument('folder_name')

        # need to check if the name already exists in the chain
        block_data = {'type': 'folder', 'name': folder_name, 'meta_hash': '', 'timestamp': time.time()}
        block = chain.update_chain(block_data)
        chain.broadcast_block(list(block))

        self.finish({'folder':folder_name, 'block': list(block)})


class RemoveFolderHandler(tornado.web.RequestHandler):
    def get(self):
        self.finish('chain test')

    @tornado.gen.coroutine
    def post(self):
        folder_name = self.get_argument('folder_name')

class UpdateFolderHandler(tornado.web.RequestHandler):
    def get(self):
        folder_name = self.get_argument('folder_name')
        names = get_folders()
        assert folder_name in names
        folder_meta_hash = names.get(folder_name)

        self.finish('''%s<br><form method="POST">
            <input name="folder_name" placeholder="Folder" />
            <input name="folder_meta_hash" placeholder="Meta Hash" />
            <input type="submit" value="Update"/></form>''' % names)

    @tornado.gen.coroutine
    def post(self):
        folder_name = self.get_argument('folder_name')
        folder_meta_hash = self.get_argument('folder_meta_hash')

        names = get_folders()
        assert folder_name in names
        # folder_meta_hash = names.get(folder_name)
        # assert folder_meta_hash
        # folder_meta_data = {'type':'folder_meta', 'name': folder_name, 'items':[]}
        # if folder_meta_hash:

        storages = get_storages()
        if not storages:
            self.finish('no storage config')
            return

        for storage_payload in storages.values():
            storage_path = storage_payload[0]
            node_name = storage_payload[1]
            with open('%s/meta/%s' % (storage_path, folder_meta_hash), 'rb') as f:
                folder_meta_json = f.read()
                folder_meta_data = tornado.escape.json_decode(folder_meta_json)
                assert folder_meta_data['type'] == 'folder_meta'

        block_data = {'type': 'folder', 'name': folder_name, 'meta_hash': folder_meta_hash, 'timestamp': time.time()}
        block = chain.update_chain(block_data)
        chain.broadcast_block(list(block))

        self.finish({})

# class RemoveFilesHandler(tornado.web.RequestHandler):
#     def get(self):
#         self.finish('chain test')


class GetMetaHandler(tornado.web.RequestHandler):
    def get(self):
        storages = get_storages()
        if not storages:
            self.finish('no storage config')
            return

        folder_meta_hash = self.get_argument('folder_meta_hash')
        for storage_path in storages.values():
            if os.path.exists('%s/meta/%s' % (storage_path, folder_meta_hash)):
                with open('%s/meta/%s' % (storage_path, folder_meta_hash), 'rb') as f:
                    folder_meta_json = f.read()
                    folder_meta_data = tornado.escape.json_decode(folder_meta_json)
                    assert folder_meta_data['type'] == 'folder_meta'
                    self.finish(folder_meta_json)
                break


class UpdateStorageHandler(tornado.web.RequestHandler):
    def get(self):
        storages = get_storages()
        self.finish('''%s<br><form method="POST">
            <input name="storage_name" placeholder="Storage Name" />
            <input name="storage_path" placeholder="Storage Path" />
            <input type="submit" value="Update" /></form>''' % storages)

    def post(self):
        storage_name = self.get_argument('storage_name')
        storage_path = self.get_argument('storage_path')

        block_data = {'type': 'storage', 'name': storage_name, 'path': storage_path, 'node_name': chain.current_name, 'timestamp': time.time()}
        block = chain.update_chain(block_data)
        chain.broadcast_block(list(block))

        self.finish({'storage': storage_name, 'block': list(block)})
