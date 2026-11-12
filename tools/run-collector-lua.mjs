// Execute existing collector fixtures with an existing Fengari dependency.
// No installs; source-file IO is restricted to a read-only in-memory snapshot.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const sha = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
const fail = code => { throw Error(code); };
try {
  const [engine, input, ...args] = process.argv.slice(2);
  if (!engine || !input) fail('USAGE_ENGINE_DIRECTORY_AND_LUA_FIXTURE');
  const test = path.resolve(root, input), relative = path.relative(root, test);
  if (relative.startsWith('..') || path.isAbsolute(relative)
    || !relative.replaceAll('\\', '/').startsWith('tools/') || !test.endsWith('.lua')
    || !fs.lstatSync(test).isFile() || fs.lstatSync(test).isSymbolicLink()) fail('FIXTURE_PATH');
  const packageFile = path.join(path.resolve(engine), 'package.json');
  const metadata = JSON.parse(fs.readFileSync(packageFile, 'utf8'));
  if (metadata.name !== 'fengari' || metadata.version !== '0.1.5') fail('ENGINE_VERSION_UNQUALIFIED');
  const require = createRequire(packageFile);
  const {lua, lauxlib, lualib, to_luastring, to_jsstring} = require('./src/fengari.js');
  const source = fs.readFileSync(test), sources = new Map();
  for (const name of fs.readdirSync(path.join(root, 'addons', 'RRECollector'))) {
    const file = path.join(root, 'addons', 'RRECollector', name);
    if (!fs.lstatSync(file).isFile() || fs.lstatSync(file).isSymbolicLink()) fail('ADDON_SOURCE_TYPE');
    sources.set('addons/RRECollector/' + name, fs.readFileSync(file));
  }
  sources.set(relative.replaceAll('\\', '/'), source);
  const hashes = Object.fromEntries([...sources].map(([name, bytes]) => [name, sha(bytes)]));
  const L = lauxlib.luaL_newstate(); lualib.luaL_openlibs(L);
  lua.lua_newtable(L);
  for (const [name, bytes] of sources) {
    for (const key of [name, path.join(root, name).replaceAll('\\', '/')]) {
      lua.lua_pushlstring(L, bytes, bytes.length); lua.lua_setfield(L, -2, to_luastring(key));
    }
  }
  lua.lua_setglobal(L, to_luastring('__RRE_SOURCES'));
  lua.lua_newtable(L);
  for (const [i, value] of [input, ...args].entries()) {
    lua.lua_pushstring(L, to_luastring(value)); lua.lua_rawseti(L, -2, i);
  }
  lua.lua_setglobal(L, to_luastring('arg'));
  const bootstrap = String.raw`
    local sources = __RRE_SOURCES; __RRE_SOURCES = nil
    local function get(file)
      if type(file) ~= 'string' then return nil end
      file = file:gsub('\\','/'):gsub('^%./','')
      return sources[file]
    end
    io.open = function(file, mode)
      if mode ~= nil and mode ~= 'r' and mode ~= 'rb' then return nil, 'fixture IO is read-only' end
      local bytes = get(file); if bytes == nil then return nil, 'source is outside fixture snapshot' end
      local closed, consumed = false, false
      return {read=function(_, pattern)
        assert(not closed and pattern == '*a', 'unsupported fixture read')
        if consumed then return '' end; consumed = true; return bytes
      end, close=function() closed = true; return true end}
    end
    loadfile = function(file)
      local bytes = get(file); if bytes == nil then return nil, 'source is outside fixture snapshot' end
      return load(bytes, '@' .. file, 't', _G)
    end
    dofile = function(file) local chunk, err = loadfile(file); assert(chunk, err); return chunk() end
    loadstring = load; unpack = table.unpack
    io.popen = nil; io.input = nil; io.output = nil; io.tmpfile = nil
    os.execute = nil; os.remove = nil; os.rename = nil; os.exit = nil
    package.loadlib = nil; package.searchers = {}
    require = function(name) local value = package.loaded[name]; assert(value ~= nil, 'fixture module unavailable'); return value end
  `;
  let status = lauxlib.luaL_dostring(L, to_luastring(bootstrap));
  if (status === lua.LUA_OK) status = lauxlib.luaL_loadbuffer(L, source, source.length, to_luastring('@' + relative));
  if (status === lua.LUA_OK) status = lua.lua_pcall(L, 0, lua.LUA_MULTRET, 0);
  const error = status === lua.LUA_OK ? null : to_jsstring(lua.lua_tostring(L, -1));
  const unchanged = [...sources].every(([name]) => sha(fs.readFileSync(path.join(root, name))) === hashes[name]);
  process.stdout.write('RRE_LUA_RESULT ' + JSON.stringify({status: status === lua.LUA_OK && unchanged ? 'passed' : 'failed',
    fixture: relative.replaceAll('\\', '/'), runtime: 'Fengari0.1.5/Lua5.3.4',
    scope: 'offline mocked Lua logic; not RIFT Lua5.1 or live UI acceptance', sourceSha256: sha(source),
    snapshotUnchanged: unchanged, error}) + '\n');
  if (status !== lua.LUA_OK || !unchanged) process.exitCode = 1;
  lua.lua_close(L);
} catch (error) {
  process.stderr.write(JSON.stringify({status: 'failed', error: /^[A-Z_]+$/.test(error?.message)
    ? error.message : 'LUA_FIXTURE_RUNTIME_UNAVAILABLE'}) + '\n');
  process.exitCode = 2;
}
