import{E as e}from"./encode-79CO1kuF.js";import{B as t}from"./index-0GPC8bPp.js";var r,n,i;try{r=new TextDecoder}catch(Ie){}var s,o,u,a,l,c=0,f={},h=0,g=0,d=[],p={useRecords:!1,mapsAsObjects:!0};class w{}const y=new w;y.name="MessagePack 0xC1";var b=!1,m=2;try{new Function("")}catch(Ie){m=1/0}class S{constructor(e){e&&(!1===e.useRecords&&void 0===e.mapsAsObjects&&(e.mapsAsObjects=!0),e.sequential&&!1!==e.trusted&&(e.trusted=!0,e.structures||0==e.useRecords||(e.structures=[],e.maxSharedStructures||(e.maxSharedStructures=0))),e.structures?e.structures.sharedLength=e.structures.length:e.getStructures&&((e.structures=[]).uninitialized=!0,e.structures.sharedLength=0),e.int64AsNumber&&(e.int64AsType="number")),Object.assign(this,e)}unpack(e,t){if(n)return Z((()=>(G(),this?this.unpack(e,t):S.prototype.unpack.call(p,e,t))));e.buffer||e.constructor!==ArrayBuffer||(e="undefined"!=typeof Buffer?Buffer.from(e):new Uint8Array(e)),"object"==typeof t?(i=t.end||e.length,c=t.start||0):(c=0,i=t>-1?t:e.length),g=0,o=null,u=null,n=e;try{l=e.dataView||(e.dataView=new DataView(e.buffer,e.byteOffset,e.byteLength))}catch(Ie){if(n=null,e instanceof Uint8Array)throw Ie;throw new Error("Source must be a Uint8Array or Buffer but was a "+(e&&"object"==typeof e?e.constructor.name:typeof e))}if(this instanceof S){if(f=this,this.structures)return s=this.structures,U(t);(!s||s.length>0)&&(s=[])}else f=p,(!s||s.length>0)&&(s=[]);return U(t)}unpackMultiple(e,t){let r,n=0;try{b=!0;let i=e.length,s=this?this.unpack(e,i):Q.unpack(e,i);if(!t){for(r=[s];c<i;)n=c,r.push(U());return r}if(!1===t(s,n,c))return;for(;c<i;)if(n=c,!1===t(U(),n,c))return}catch(Ie){throw Ie.lastPosition=n,Ie.values=r,Ie}finally{b=!1,G()}}_mergeStructures(e,t){e=e||[],Object.isFrozen(e)&&(e=e.map((e=>e.slice(0))));for(let r=0,n=e.length;r<n;r++){let t=e[r];t&&(t.isShared=!0,r>=32&&(t.highByte=r-32>>5))}e.sharedLength=e.length;for(let r in t||[])if(r>=0){let n=e[r],i=t[r];i&&(n&&((e.restoreStructures||(e.restoreStructures=[]))[r]=n),e[r]=i)}return this.structures=e}decode(e,t){return this.unpack(e,t)}}function U(e){try{if(!f.trusted&&!b){let e=s.sharedLength||0;e<s.length&&(s.length=e)}let e;if(f.randomAccessStructure&&n[c]<64&&n[c],e=A(),u&&(c=u.postBundlePosition,u=null),b&&(s.restoreStructures=null),c==i)s&&s.restoreStructures&&v(),s=null,n=null,a&&(a=null);else{if(c>i)throw new Error("Unexpected end of MessagePack data");if(!b){let t;try{t=JSON.stringify(e,((e,t)=>"bigint"==typeof t?`${t}n`:t)).slice(0,100)}catch(Ie){t="(JSON view not available "+Ie+")"}throw new Error("Data read, but end of buffer not reached "+t)}}return e}catch(Ie){throw s&&s.restoreStructures&&v(),G(),(Ie instanceof RangeError||Ie.message.startsWith("Unexpected end of buffer")||c>i)&&(Ie.incomplete=!0),Ie}}function v(){for(let e in s.restoreStructures)s[e]=s.restoreStructures[e];s.restoreStructures=null}function A(){let e=n[c++];if(e<160){if(e<128){if(e<64)return e;{let t=s[63&e]||f.getStructures&&I()[63&e];return t?(t.read||(t.read=k(t,63&e)),t.read()):e}}if(e<144){if(e-=128,f.mapsAsObjects){let t={};for(let r=0;r<e;r++){let e=P();"__proto__"===e&&(e="__proto_"),t[e]=A()}return t}{let t=new Map;for(let r=0;r<e;r++)t.set(A(),A());return t}}{e-=144;let t=new Array(e);for(let r=0;r<e;r++)t[r]=A();return f.freezeData?Object.freeze(t):t}}if(e<192){let t=e-160;if(g>=c)return o.slice(c-h,(c+=t)-h);if(0==g&&i<140){let e=t<16?V(t):D(t);if(null!=e)return e}return _(t)}{let t;switch(e){case 192:return null;case 193:return u?(t=A(),t>0?u[1].slice(u.position1,u.position1+=t):u[0].slice(u.position0,u.position0-=t)):y;case 194:return!1;case 195:return!0;case 196:if(t=n[c++],void 0===t)throw new Error("Unexpected end of buffer");return z(t);case 197:return t=l.getUint16(c),c+=2,z(t);case 198:return t=l.getUint32(c),c+=4,z(t);case 199:return C(n[c++]);case 200:return t=l.getUint16(c),c+=2,C(t);case 201:return t=l.getUint32(c),c+=4,C(t);case 202:if(t=l.getFloat32(c),f.useFloat32>2){let e=H[(127&n[c])<<1|n[c+1]>>7];return c+=4,(e*t+(t>0?.5:-.5)>>0)/e}return c+=4,t;case 203:return t=l.getFloat64(c),c+=8,t;case 204:return n[c++];case 205:return t=l.getUint16(c),c+=2,t;case 206:return t=l.getUint32(c),c+=4,t;case 207:return"number"===f.int64AsType?(t=4294967296*l.getUint32(c),t+=l.getUint32(c+4)):"string"===f.int64AsType?t=l.getBigUint64(c).toString():"auto"===f.int64AsType?(t=l.getBigUint64(c),t<=BigInt(2)<<BigInt(52)&&(t=Number(t))):t=l.getBigUint64(c),c+=8,t;case 208:return l.getInt8(c++);case 209:return t=l.getInt16(c),c+=2,t;case 210:return t=l.getInt32(c),c+=4,t;case 211:return"number"===f.int64AsType?(t=4294967296*l.getInt32(c),t+=l.getUint32(c+4)):"string"===f.int64AsType?t=l.getBigInt64(c).toString():"auto"===f.int64AsType?(t=l.getBigInt64(c),t>=BigInt(-2)<<BigInt(52)&&t<=BigInt(2)<<BigInt(52)&&(t=Number(t))):t=l.getBigInt64(c),c+=8,t;case 212:if(t=n[c++],114==t)return J(63&n[c++]);{let e=d[t];if(e)return e.read?(c++,e.read(A())):e.noBuffer?(c++,e()):e(n.subarray(c,++c));throw new Error("Unknown extension "+t)}case 213:return t=n[c],114==t?(c++,J(63&n[c++],n[c++])):C(2);case 214:return C(4);case 215:return C(8);case 216:return C(16);case 217:return t=n[c++],g>=c?o.slice(c-h,(c+=t)-h):x(t);case 218:return t=l.getUint16(c),g>=(c+=2)?o.slice(c-h,(c+=t)-h):E(t);case 219:return t=l.getUint32(c),g>=(c+=4)?o.slice(c-h,(c+=t)-h):j(t);case 220:return t=l.getUint16(c),c+=2,M(t);case 221:return t=l.getUint32(c),c+=4,M(t);case 222:return t=l.getUint16(c),c+=2,R(t);case 223:return t=l.getUint32(c),c+=4,R(t);default:if(e>=224)return e-256;if(void 0===e){let e=new Error("Unexpected end of MessagePack data");throw e.incomplete=!0,e}throw new Error("Unknown MessagePack token "+e)}}}const B=/^[a-zA-Z_$][a-zA-Z\d_$]*$/;function k(e,t){function r(){if(r.count++>m){let r=e.read=new Function("r","return function(){return "+(f.freezeData?"Object.freeze":"")+"({"+e.map((e=>"__proto__"===e?"__proto_:r()":B.test(e)?e+":r()":"["+JSON.stringify(e)+"]:r()")).join(",")+"})}")(A);return 0===e.highByte&&(e.read=O(t,e.read)),r()}let n={};for(let t=0,r=e.length;t<r;t++){let r=e[t];"__proto__"===r&&(r="__proto_"),n[r]=A()}return f.freezeData?Object.freeze(n):n}return r.count=0,0===e.highByte?O(t,r):r}const O=(e,t)=>function(){let r=n[c++];if(0===r)return t();let i=e<32?-(e+(r<<5)):e+(r<<5),o=s[i]||I()[i];if(!o)throw new Error("Record id is not defined for "+i);return o.read||(o.read=k(o,e)),o.read()};function I(){let e=Z((()=>(n=null,f.getStructures())));return s=f._mergeStructures(e,s)}var _=T,x=T,E=T,j=T;function T(e){let t;if(e<16&&(t=V(e)))return t;if(e>64&&r)return r.decode(n.subarray(c,c+=e));const i=c+e,s=[];for(t="";c<i;){const e=n[c++];if(0==(128&e))s.push(e);else if(192==(224&e)){const t=63&n[c++];s.push((31&e)<<6|t)}else if(224==(240&e)){const t=63&n[c++],r=63&n[c++];s.push((31&e)<<12|t<<6|r)}else if(240==(248&e)){let t=(7&e)<<18|(63&n[c++])<<12|(63&n[c++])<<6|63&n[c++];t>65535&&(t-=65536,s.push(t>>>10&1023|55296),t=56320|1023&t),s.push(t)}else s.push(e);s.length>=4096&&(t+=N.apply(String,s),s.length=0)}return s.length>0&&(t+=N.apply(String,s)),t}function M(e){let t=new Array(e);for(let r=0;r<e;r++)t[r]=A();return f.freezeData?Object.freeze(t):t}function R(e){if(f.mapsAsObjects){let t={};for(let r=0;r<e;r++){let e=P();"__proto__"===e&&(e="__proto_"),t[e]=A()}return t}{let t=new Map;for(let r=0;r<e;r++)t.set(A(),A());return t}}var N=String.fromCharCode;function D(e){let t=c,r=new Array(e);for(let i=0;i<e;i++){const e=n[c++];if((128&e)>0)return void(c=t);r[i]=e}return N.apply(String,r)}function V(e){if(e<4){if(e<2){if(0===e)return"";{let e=n[c++];return(128&e)>1?void(c-=1):N(e)}}{let t=n[c++],r=n[c++];if((128&t)>0||(128&r)>0)return void(c-=2);if(e<3)return N(t,r);let i=n[c++];return(128&i)>0?void(c-=3):N(t,r,i)}}{let t=n[c++],r=n[c++],i=n[c++],s=n[c++];if((128&t)>0||(128&r)>0||(128&i)>0||(128&s)>0)return void(c-=4);if(e<6){if(4===e)return N(t,r,i,s);{let e=n[c++];return(128&e)>0?void(c-=5):N(t,r,i,s,e)}}if(e<8){let o=n[c++],u=n[c++];if((128&o)>0||(128&u)>0)return void(c-=6);if(e<7)return N(t,r,i,s,o,u);let a=n[c++];return(128&a)>0?void(c-=7):N(t,r,i,s,o,u,a)}{let o=n[c++],u=n[c++],a=n[c++],l=n[c++];if((128&o)>0||(128&u)>0||(128&a)>0||(128&l)>0)return void(c-=8);if(e<10){if(8===e)return N(t,r,i,s,o,u,a,l);{let e=n[c++];return(128&e)>0?void(c-=9):N(t,r,i,s,o,u,a,l,e)}}if(e<12){let f=n[c++],h=n[c++];if((128&f)>0||(128&h)>0)return void(c-=10);if(e<11)return N(t,r,i,s,o,u,a,l,f,h);let g=n[c++];return(128&g)>0?void(c-=11):N(t,r,i,s,o,u,a,l,f,h,g)}{let f=n[c++],h=n[c++],g=n[c++],d=n[c++];if((128&f)>0||(128&h)>0||(128&g)>0||(128&d)>0)return void(c-=12);if(e<14){if(12===e)return N(t,r,i,s,o,u,a,l,f,h,g,d);{let e=n[c++];return(128&e)>0?void(c-=13):N(t,r,i,s,o,u,a,l,f,h,g,d,e)}}{let p=n[c++],w=n[c++];if((128&p)>0||(128&w)>0)return void(c-=14);if(e<15)return N(t,r,i,s,o,u,a,l,f,h,g,d,p,w);let y=n[c++];return(128&y)>0?void(c-=15):N(t,r,i,s,o,u,a,l,f,h,g,d,p,w,y)}}}}}function F(){let e,t=n[c++];if(t<192)e=t-160;else switch(t){case 217:e=n[c++];break;case 218:e=l.getUint16(c),c+=2;break;case 219:e=l.getUint32(c),c+=4;break;default:throw new Error("Expected string")}return T(e)}function z(e){return f.copyBuffers?Uint8Array.prototype.slice.call(n,c,c+=e):n.subarray(c,c+=e)}function C(e){let t=n[c++];if(d[t]){let r;return d[t](n.subarray(c,r=c+=e),(e=>{c=e;try{return A()}finally{c=r}}))}throw new Error("Unknown extension type "+t)}var L=new Array(4096);function P(){let e=n[c++];if(!(e>=160&&e<192))return c--,A().toString();if(e-=160,g>=c)return o.slice(c-h,(c+=e)-h);if(!(0==g&&i<180))return _(e);let t,r=4095&(e<<5^(e>1?l.getUint16(c):e>0?n[c]:0)),s=L[r],u=c,a=c+e-3,f=0;if(s&&s.bytes==e){for(;u<a;){if(t=l.getUint32(u),t!=s[f++]){u=1879048192;break}u+=4}for(a+=3;u<a;)if(t=n[u++],t!=s[f++]){u=1879048192;break}if(u===a)return c=u,s.string;a-=3,u=c}for(s=[],L[r]=s,s.bytes=e;u<a;)t=l.getUint32(u),s.push(t),u+=4;for(a+=3;u<a;)t=n[u++],s.push(t);let d=e<16?V(e):D(e);return s.string=null!=d?d:_(e)}const J=(e,t)=>{let r=A().map((e=>e.toString())),n=e;void 0!==t&&(e=e<32?-((t<<5)+e):(t<<5)+e,r.highByte=t);let i=s[e];return i&&(i.isShared||b)&&((s.restoreStructures||(s.restoreStructures=[]))[e]=i),s[e]=r,r.read=k(r,n),r.read()};d[0]=()=>{},d[0].noBuffer=!0,d[66]=e=>{let t=e.length,r=BigInt(128&e[0]?e[0]-256:e[0]);for(let n=1;n<t;n++)r<<=8n,r+=BigInt(e[n]);return r};let W={Error:Error,TypeError:TypeError,ReferenceError:ReferenceError};d[101]=()=>{let e=A();return(W[e[0]]||Error)(e[1])},d[105]=e=>{let t=l.getUint32(c-4);a||(a=new Map);let r,i=n[c];r=i>=144&&i<160||220==i||221==i?[]:{};let s={target:r};a.set(t,s);let o=A();return s.used?Object.assign(r,o):(s.target=o,o)},d[112]=e=>{let t=l.getUint32(c-4),r=a.get(t);return r.used=!0,r.target},d[115]=()=>new Set(A());const $=["Int8","Uint8","Uint8Clamped","Int16","Uint16","Int32","Uint32","Float32","Float64","BigInt64","BigUint64"].map((e=>e+"Array"));let q="object"==typeof globalThis?globalThis:window;d[116]=e=>{let t=e[0],r=$[t];if(!r)throw new Error("Could not find typed array for code "+t);return new q[r](Uint8Array.prototype.slice.call(e,1).buffer)},d[120]=()=>{let e=A();return new RegExp(e[0],e[1])};const K=[];function Z(e){let t=i,r=c,d=h,p=g,w=o,y=a,m=u,S=new Uint8Array(n.slice(0,i)),U=s,v=s.slice(0,s.length),A=f,B=b,k=e();return i=t,c=r,h=d,g=p,o=w,a=y,u=m,n=S,b=B,(s=U).splice(0,s.length,...v),f=A,l=new DataView(n.buffer,n.byteOffset,n.byteLength),k}function G(){n=null,a=null,s=null}d[98]=e=>{let t=(e[0]<<24)+(e[1]<<16)+(e[2]<<8)+e[3],r=c;return c+=t-e.length,u=K,(u=[F(),F()]).position0=0,u.position1=0,u.postBundlePosition=c,c=r,A()},d[255]=e=>4==e.length?new Date(1e3*(16777216*e[0]+(e[1]<<16)+(e[2]<<8)+e[3])):8==e.length?new Date(((e[0]<<22)+(e[1]<<14)+(e[2]<<6)+(e[3]>>2))/1e6+1e3*(4294967296*(3&e[3])+16777216*e[4]+(e[5]<<16)+(e[6]<<8)+e[7])):12==e.length?new Date(((e[0]<<24)+(e[1]<<16)+(e[2]<<8)+e[3])/1e6+1e3*((128&e[4]?-281474976710656:0)+1099511627776*e[6]+4294967296*e[7]+16777216*e[8]+(e[9]<<16)+(e[10]<<8)+e[11])):new Date("invalid");const H=new Array(147);for(let _e=0;_e<256;_e++)H[_e]=+("1e"+Math.floor(45.15-.30103*_e));var Q=new S({useRecords:!1});Q.unpack,Q.unpackMultiple,Q.unpack;let X,Y,ee,te=new Float32Array(1);new Uint8Array(te.buffer,0,4);try{X=new TextEncoder}catch(Ie){}const re="undefined"!=typeof Buffer,ne=re?function(e){return Buffer.allocUnsafeSlow(e)}:Uint8Array,ie=re?Buffer:Uint8Array,se=re?4294967296:2144337920;let oe,ue,ae,le,ce=0,fe=null;const he=/[\u0080-\uFFFF]/,ge=Symbol("record-id");class de extends S{constructor(e){let t,r,n,i;super(e),this.offset=0;let s=ie.prototype.utf8Write?function(e,t){return oe.utf8Write(e,t,4294967295)}:!(!X||!X.encodeInto)&&function(e,t){return X.encodeInto(e,oe.subarray(t)).written},o=this;e||(e={});let u=e&&e.sequential,a=e.structures||e.saveStructures,l=e.maxSharedStructures;if(null==l&&(l=a?32:0),l>8160)throw new Error("Maximum maxSharedStructure is 8160");e.structuredClone&&null==e.moreTypes&&(this.moreTypes=!0);let c=e.maxOwnStructures;null==c&&(c=a?32:64),this.structures||0==e.useRecords||(this.structures=[]);let f=l>32||c+l>64,h=l+64,g=l+c+64;if(g>8256)throw new Error("Maximum maxSharedStructure + maxOwnStructure is 8192");let d=[],p=0,w=0;this.pack=this.encode=function(e,s){if(oe||(oe=new ne(8192),ae=oe.dataView||(oe.dataView=new DataView(oe.buffer,0,8192)),ce=0),le=oe.length-10,le-ce<2048?(oe=new ne(oe.length),ae=oe.dataView||(oe.dataView=new DataView(oe.buffer,0,oe.length)),le=oe.length-10,ce=0):ce=ce+7&2147483640,t=ce,s&Ae&&(ce+=255&s),i=o.structuredClone?new Map:null,o.bundleStrings&&"string"!=typeof e?(fe=[],fe.size=1/0):fe=null,n=o.structures,n){n.uninitialized&&(n=o._mergeStructures(o.getStructures()));let e=n.sharedLength||0;if(e>l)throw new Error("Shared structures is larger than maximum shared structures, try increasing maxSharedStructures to "+n.sharedLength);if(!n.transitions){n.transitions=Object.create(null);for(let t=0;t<e;t++){let e=n[t];if(!e)continue;let r,i=n.transitions;for(let t=0,n=e.length;t<n;t++){let n=e[t];r=i[n],r||(r=i[n]=Object.create(null)),i=r}i[ge]=t+64}this.lastNamedStructuresLength=e}u||(n.nextId=e+64)}let a;r&&(r=!1);try{o.randomAccessStructure&&e&&e.constructor&&e.constructor===Object?I(e):m(e);let r=fe;if(fe&&be(t,m,0),i&&i.idsToInsert){let e=i.idsToInsert.sort(((e,t)=>e.offset>t.offset?1:-1)),n=e.length,s=-1;for(;r&&n>0;){let i=e[--n].offset+t;i<r.stringsPosition+t&&-1===s&&(s=0),i>r.position+t?s>=0&&(s+=6):(s>=0&&(ae.setUint32(r.position+t,ae.getUint32(r.position+t)+s),s=-1),r=r.previous,n++)}s>=0&&r&&ae.setUint32(r.position+t,ae.getUint32(r.position+t)+s),ce+=6*e.length,ce>le&&B(ce),o.offset=ce;let u=function(e,t){let r,n=6*t.length,i=e.length-n;for(;r=t.pop();){let t=r.offset,s=r.id;e.copyWithin(t+n,t,i),n-=6;let o=t+n;e[o++]=214,e[o++]=105,e[o++]=s>>24,e[o++]=s>>16&255,e[o++]=s>>8&255,e[o++]=255&s,i=t}return e}(oe.subarray(t,ce),e);return i=null,u}return o.offset=ce,s&Ue?(oe.start=t,oe.end=ce,oe):oe.subarray(t,ce)}catch(Ie){throw a=Ie,Ie}finally{if(n&&(y(),r&&o.saveStructures)){let r=n.sharedLength||0,i=oe.subarray(t,ce),u=function(e,t){return e.isCompatible=e=>{let r=!e||(t.lastNamedStructuresLength||0)===e.length;return r||t._mergeStructures(e),r},e}(n,o);if(!a)return!1===o.saveStructures(u,u.isCompatible)?o.pack(e,s):(o.lastNamedStructuresLength=r,i)}s&ve&&(ce=t)}};const y=()=>{w<10&&w++;let e=n.sharedLength||0;if(n.length>e&&!u&&(n.length=e),p>1e4)n.transitions=null,w=0,p=0,d.length>0&&(d=[]);else if(d.length>0&&!u){for(let e=0,t=d.length;e<t;e++)d[e][ge]=0;d=[]}},b=e=>{var t=e.length;t<16?oe[ce++]=144|t:t<65536?(oe[ce++]=220,oe[ce++]=t>>8,oe[ce++]=255&t):(oe[ce++]=221,ae.setUint32(ce,t),ce+=4);for(let r=0;r<t;r++)m(e[r])},m=e=>{ce>le&&(oe=B(ce));var r,n=typeof e;if("string"===n){let n,i=e.length;if(fe&&i>=4&&i<4096){if((fe.size+=i)>21760){let e,r,n=(fe[0]?3*fe[0].length+fe[1].length:0)+10;ce+n>le&&(oe=B(ce+n)),fe.position?(r=fe,oe[ce]=200,ce+=3,oe[ce++]=98,e=ce-t,ce+=4,be(t,m,0),ae.setUint16(e+t-3,ce-t-e)):(oe[ce++]=214,oe[ce++]=98,e=ce-t,ce+=4),fe=["",""],fe.previous=r,fe.size=0,fe.position=e}let r=he.test(e);return fe[r?0:1]+=e,oe[ce++]=193,void m(r?-i:i)}n=i<32?1:i<256?2:i<65536?3:5;let o=3*i;if(ce+o>le&&(oe=B(ce+o)),i<64||!s){let t,s,o,u=ce+n;for(t=0;t<i;t++)s=e.charCodeAt(t),s<128?oe[u++]=s:s<2048?(oe[u++]=s>>6|192,oe[u++]=63&s|128):55296==(64512&s)&&56320==(64512&(o=e.charCodeAt(t+1)))?(s=65536+((1023&s)<<10)+(1023&o),t++,oe[u++]=s>>18|240,oe[u++]=s>>12&63|128,oe[u++]=s>>6&63|128,oe[u++]=63&s|128):(oe[u++]=s>>12|224,oe[u++]=s>>6&63|128,oe[u++]=63&s|128);r=u-ce-n}else r=s(e,ce+n);r<32?oe[ce++]=160|r:r<256?(n<2&&oe.copyWithin(ce+2,ce+1,ce+1+r),oe[ce++]=217,oe[ce++]=r):r<65536?(n<3&&oe.copyWithin(ce+3,ce+2,ce+2+r),oe[ce++]=218,oe[ce++]=r>>8,oe[ce++]=255&r):(n<5&&oe.copyWithin(ce+5,ce+3,ce+3+r),oe[ce++]=219,ae.setUint32(ce,r),ce+=4),ce+=r}else if("number"===n)if(e>>>0===e)e<32||e<128&&!1===this.useRecords||e<64&&!this.randomAccessStructure?oe[ce++]=e:e<256?(oe[ce++]=204,oe[ce++]=e):e<65536?(oe[ce++]=205,oe[ce++]=e>>8,oe[ce++]=255&e):(oe[ce++]=206,ae.setUint32(ce,e),ce+=4);else if(e>>0===e)e>=-32?oe[ce++]=256+e:e>=-128?(oe[ce++]=208,oe[ce++]=e+256):e>=-32768?(oe[ce++]=209,ae.setInt16(ce,e),ce+=2):(oe[ce++]=210,ae.setInt32(ce,e),ce+=4);else{let t;if((t=this.useFloat32)>0&&e<4294967296&&e>=-2147483648){let r;if(oe[ce++]=202,ae.setFloat32(ce,e),t<4||(r=e*H[(127&oe[ce])<<1|oe[ce+1]>>7])>>0===r)return void(ce+=4);ce--}oe[ce++]=203,ae.setFloat64(ce,e),ce+=8}else if("object"===n||"function"===n)if(e){if(i){let r=i.get(e);if(r){if(!r.id){let e=i.idsToInsert||(i.idsToInsert=[]);r.id=e.push(r)}return oe[ce++]=214,oe[ce++]=112,ae.setUint32(ce,r.id),void(ce+=4)}i.set(e,{offset:ce-t})}let s=e.constructor;if(s===Object)A(e,!0);else if(s===Array)b(e);else if(s===Map)if(this.mapAsEmptyObject)oe[ce++]=128;else{(r=e.size)<16?oe[ce++]=128|r:r<65536?(oe[ce++]=222,oe[ce++]=r>>8,oe[ce++]=255&r):(oe[ce++]=223,ae.setUint32(ce,r),ce+=4);for(let[t,r]of e)m(t),m(r)}else{for(let t=0,r=Y.length;t<r;t++){if(e instanceof ee[t]){let r=Y[t];if(r.write){r.type&&(oe[ce++]=212,oe[ce++]=r.type,oe[ce++]=0);let t=r.write.call(this,e);return void(t===e?Array.isArray(e)?b(e):A(e):m(t))}let n,i=oe,s=ae,o=ce;oe=null;try{n=r.pack.call(this,e,(e=>(oe=i,i=null,ce+=e,ce>le&&B(ce),{target:oe,targetView:ae,position:ce-e})),m)}finally{i&&(oe=i,ae=s,ce=o,le=oe.length-10)}return void(n&&(n.length+ce>le&&B(n.length+ce),ce=ye(n,oe,ce,r.type)))}}if(Array.isArray(e))b(e);else{if(e.toJSON){const t=e.toJSON();if(t!==e)return m(t)}if("function"===n)return m(this.writeFunction&&this.writeFunction(e));A(e,!e.hasOwnProperty)}}}else oe[ce++]=192;else if("boolean"===n)oe[ce++]=e?195:194;else if("bigint"===n){if(e<BigInt(1)<<BigInt(63)&&e>=-(BigInt(1)<<BigInt(63)))oe[ce++]=211,ae.setBigInt64(ce,e);else if(e<BigInt(1)<<BigInt(64)&&e>0)oe[ce++]=207,ae.setBigUint64(ce,e);else{if(!this.largeBigIntToFloat){if(this.useBigIntExtension&&e<2n**1023n&&e>-(2n**1023n)){oe[ce++]=199,ce++,oe[ce++]=66;let t,r=[];do{let n=0xffn&e;t=(0x80n&n)===(e<0n?0x80n:0n),r.push(n),e>>=8n}while(0n!==e&&-1n!==e||!t);oe[ce-2]=r.length;for(let e=r.length;e>0;)oe[ce++]=Number(r[--e]);return}throw new RangeError(e+" was too large to fit in MessagePack 64-bit integer format, use useBigIntExtension or set largeBigIntToFloat to convert to float-64")}oe[ce++]=203,ae.setFloat64(ce,Number(e))}ce+=8}else{if("undefined"!==n)throw new Error("Unknown type: "+n);this.encodeUndefinedAsNil?oe[ce++]=192:(oe[ce++]=212,oe[ce++]=0,oe[ce++]=0)}},S=this.variableMapSize||this.coercibleKeyAsNumber?e=>{let t,r=Object.keys(e),n=r.length;if(n<16?oe[ce++]=128|n:n<65536?(oe[ce++]=222,oe[ce++]=n>>8,oe[ce++]=255&n):(oe[ce++]=223,ae.setUint32(ce,n),ce+=4),this.coercibleKeyAsNumber)for(let i=0;i<n;i++){t=r[i];let n=Number(t);m(isNaN(n)?t:n),m(e[t])}else for(let i=0;i<n;i++)m(t=r[i]),m(e[t])}:(e,r)=>{oe[ce++]=222;let n=ce-t;ce+=2;let i=0;for(let t in e)(r||e.hasOwnProperty(t))&&(m(t),m(e[t]),i++);oe[n+++t]=i>>8,oe[n+t]=255&i},U=!1===this.useRecords?S:e.progressiveRecords&&!f?(e,r)=>{let i,s,o=n.transitions||(n.transitions=Object.create(null)),u=ce++-t;for(let a in e)if(r||e.hasOwnProperty(a)){if(i=o[a],i)o=i;else{let r=Object.keys(e),l=o;o=n.transitions;let c=0;for(let e=0,t=r.length;e<t;e++){let t=r[e];i=o[t],i||(i=o[t]=Object.create(null),c++),o=i}u+t+1==ce?(ce--,k(o,r,c)):O(o,r,u,c),s=!0,o=l[a]}m(e[a])}if(!s){let r=o[ge];r?oe[u+t]=r:O(o,Object.keys(e),u,0)}}:(e,t)=>{let r,i=n.transitions||(n.transitions=Object.create(null)),s=0;for(let n in e)(t||e.hasOwnProperty(n))&&(r=i[n],r||(r=i[n]=Object.create(null),s++),i=r);let o=i[ge];o?o>=96&&f?(oe[ce++]=96+(31&(o-=96)),oe[ce++]=o>>5):oe[ce++]=o:k(i,i.__keys__||Object.keys(e),s);for(let n in e)(t||e.hasOwnProperty(n))&&m(e[n])},v="function"==typeof this.useRecords&&this.useRecords,A=v?(e,t)=>{v(e)?U(e,t):S(e,t)}:U,B=e=>{let r;if(e>16777216){if(e-t>se)throw new Error("Packed buffer would be larger than maximum buffer size");r=Math.min(se,4096*Math.round(Math.max((e-t)*(e>67108864?1.25:2),4194304)/4096))}else r=1+(Math.max(e-t<<2,oe.length-1)>>12)<<12;let n=new ne(r);return ae=n.dataView||(n.dataView=new DataView(n.buffer,0,r)),e=Math.min(e,oe.length),oe.copy?oe.copy(n,0,t,e):n.set(oe.slice(t,e)),ce-=t,t=0,le=n.length-10,oe=n},k=(e,t,i)=>{let s=n.nextId;s||(s=64),s<h&&this.shouldShareStructure&&!this.shouldShareStructure(t)?(s=n.nextOwnId,s<g||(s=h),n.nextOwnId=s+1):(s>=g&&(s=h),n.nextId=s+1);let o=t.highByte=s>=96&&f?s-96>>5:-1;e[ge]=s,e.__keys__=t,n[s-64]=t,s<h?(t.isShared=!0,n.sharedLength=s-63,r=!0,o>=0?(oe[ce++]=96+(31&s),oe[ce++]=o):oe[ce++]=s):(o>=0?(oe[ce++]=213,oe[ce++]=114,oe[ce++]=96+(31&s),oe[ce++]=o):(oe[ce++]=212,oe[ce++]=114,oe[ce++]=s),i&&(p+=w*i),d.length>=c&&(d.shift()[ge]=0),d.push(e),m(t))},O=(e,r,n,i)=>{let s=oe,o=ce,u=le,a=t;oe=ue,ce=0,t=0,oe||(ue=oe=new ne(8192)),le=oe.length-10,k(e,r,i),ue=oe;let l=ce;if(oe=s,ce=o,le=u,t=a,l>1){let e=ce+l-1;e>le&&B(e);let r=n+t;oe.copyWithin(r+l,r+1,ce),oe.set(ue.slice(0,l),r),ce=e}else oe[n+t]=ue[0]},I=(e,i)=>{let s=undefined(e,oe,t,ce,n,B,((e,t,n)=>{if(n)return r=!0;ce=t;let i=oe;return m(e),y(),i!==oe?{position:ce,targetView:ae,target:oe}:ce}),this);if(0===s)return A(e,!0);ce=s}}useBuffer(e){oe=e,ae=new DataView(oe.buffer,oe.byteOffset,oe.byteLength),ce=0}clearSharedData(){this.structures&&(this.structures=[]),this.typedStructs&&(this.typedStructs=[])}}function pe(e,t,r,n){let i=e.byteLength;if(i+1<256){var{target:s,position:o}=r(4+i);s[o++]=199,s[o++]=i+1}else if(i+1<65536){var{target:s,position:o}=r(5+i);s[o++]=200,s[o++]=i+1>>8,s[o++]=i+1&255}else{var{target:s,position:o,targetView:u}=r(7+i);s[o++]=201,u.setUint32(o,i+1),o+=4}s[o++]=116,s[o++]=t,s.set(new Uint8Array(e.buffer,e.byteOffset,e.byteLength),o)}function we(e,t){let r=e.byteLength;var n,i;if(r<256){var{target:n,position:i}=t(r+2);n[i++]=196,n[i++]=r}else if(r<65536){var{target:n,position:i}=t(r+3);n[i++]=197,n[i++]=r>>8,n[i++]=255&r}else{var{target:n,position:i,targetView:s}=t(r+5);n[i++]=198,s.setUint32(i,r),i+=4}n.set(e,i)}function ye(e,t,r,n){let i=e.length;switch(i){case 1:t[r++]=212;break;case 2:t[r++]=213;break;case 4:t[r++]=214;break;case 8:t[r++]=215;break;case 16:t[r++]=216;break;default:i<256?(t[r++]=199,t[r++]=i):i<65536?(t[r++]=200,t[r++]=i>>8,t[r++]=255&i):(t[r++]=201,t[r++]=i>>24,t[r++]=i>>16&255,t[r++]=i>>8&255,t[r++]=255&i)}return t[r++]=n,t.set(e,r),r+=i}function be(e,t,r){if(fe.length>0){ae.setUint32(fe.position+e,ce+r-fe.position-e),fe.stringsPosition=ce-e;let n=fe;fe=null,t(n[0]),t(n[1])}}ee=[Date,Set,Error,RegExp,ArrayBuffer,Object.getPrototypeOf(Uint8Array.prototype).constructor,w],Y=[{pack(e,t,r){let n=e.getTime()/1e3;if((this.useTimestamp32||0===e.getMilliseconds())&&n>=0&&n<4294967296){let{target:e,targetView:r,position:i}=t(6);e[i++]=214,e[i++]=255,r.setUint32(i,n)}else if(n>0&&n<4294967296){let{target:r,targetView:i,position:s}=t(10);r[s++]=215,r[s++]=255,i.setUint32(s,4e6*e.getMilliseconds()+(n/1e3/4294967296>>0)),i.setUint32(s+4,n)}else if(isNaN(n)){if(this.onInvalidDate)return t(0),r(this.onInvalidDate());let{target:e,targetView:n,position:i}=t(3);e[i++]=212,e[i++]=255,e[i++]=255}else{let{target:r,targetView:i,position:s}=t(15);r[s++]=199,r[s++]=12,r[s++]=255,i.setUint32(s,1e6*e.getMilliseconds()),i.setBigInt64(s+4,BigInt(Math.floor(n)))}}},{pack(e,t,r){if(this.setAsEmptyObject)return t(0),r({});let n=Array.from(e),{target:i,position:s}=t(this.moreTypes?3:0);this.moreTypes&&(i[s++]=212,i[s++]=115,i[s++]=0),r(n)}},{pack(e,t,r){let{target:n,position:i}=t(this.moreTypes?3:0);this.moreTypes&&(n[i++]=212,n[i++]=101,n[i++]=0),r([e.name,e.message])}},{pack(e,t,r){let{target:n,position:i}=t(this.moreTypes?3:0);this.moreTypes&&(n[i++]=212,n[i++]=120,n[i++]=0),r([e.source,e.flags])}},{pack(e,t){this.moreTypes?pe(e,16,t):we(re?Buffer.from(e):new Uint8Array(e),t)}},{pack(e,t){let r=e.constructor;r!==ie&&this.moreTypes?pe(e,$.indexOf(r.name),t):we(e,t)}},{pack(e,t){let{target:r,position:n}=t(1);r[n]=193}}];let me=new de({useRecords:!1});me.pack,me.pack;const Se=de,Ue=512,ve=1024,Ae=2048;async function Be(){await Oe((()=>({a:1e3,b:!0,c:{d:{e:{f:1e3}}},z:new Uint8Array([34,0,0,0,241,98,92,191,255,255,255,255,4,0,109,234,6,20,109,247,209,11,107,30,34,15,110,220,163,50,204,3,129,30,173,43,0,2,86,104,65,63,27,191,23,23])})))}class ke extends t{encode;decode;data;encodedData;constructor(e,t,r){super(),this.encode=t,this.decode=r,this.data=e,this.encodedData=t(e)}async encoding(){return this.encode(this.data)}async decoding(){return this.decode(this.encodedData)}}const Oe=async t=>{let r=new e,n=new Se;new e({structuredClone:!0}),new Se({structuredClone:!0}),new e({structuredClone:!0,useRecords:!0}),new Se({structuredClone:!0,useRecords:!0}),new e({structuredClone:!0,structures:[]}),new e({structuredClone:!0,structures:[],useRecords:!0}),new e({structures:[],useRecords:!0}),new Se({structuredClone:!0,structures:[]}),new Se({structuredClone:!0,structures:[],useRecords:!0}),new Se({structures:[],useRecords:!0}),new Array,await new ke(t(),JSON.stringify,JSON.parse).run({name:"JSON"}),await new ke(t(),r.encode.bind(r),r.decode.bind(r)).run({name:"CBOR"}),await new ke(t(),n.encode.bind(n),n.decode.bind(n)).run({name:"MSGPack"})};export{Be as m};
//# sourceMappingURL=index-XwBnzzjP.js.map