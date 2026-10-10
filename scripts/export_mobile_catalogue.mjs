// Reviewed ES modules are the authoring source. The backend uses this inert snapshot.
import {courses} from '../public/mobile/course.mjs';
import {writeFileSync} from 'node:fs';
writeFileSync(new URL('../public/mobile/catalogue.json',import.meta.url),JSON.stringify(courses,null,2)+'\n');
