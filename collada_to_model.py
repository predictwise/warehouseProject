#!/usr/bin/env python -Wignore

from __future__ import print_function
import collada
from numpy import array, concatenate, empty
import sys
from os import path
import argparse


class ColladaToModel(object):
    """
    Converts a COLLADA file into lists of textures, vertices, normals, and
    triangles, and can write out a .model file.
    """
    def __init__(self, filename, ignore=False):
        # Ignore errors if ignore flag is True
        ignore = []
        if ignore:
            ignore.extend([
                collada.DaeUnsupportedError, 
                collada.DaeBrokenRefError,
            ])

        self.name, ext = path.splitext(path.basename(filename))

        # Parse the Collada file
        self.scene = collada.Collada(filename, ignore=ignore)

        if self.scene.errors:
            print(*self.scene.errors, sep='\n', file=sys.stderr)

        self.textures = []
        self._vertices = empty((0, 3))
        self.normals = []
        self.triangles = []
        num = 0
        for i, triangle in enumerate(self.get_triangles()):
            
            # Create triangle indices, pretending all vertices and normals are unique
            vertex_ind = array([0, 1, 2]) + len(self._vertices)
            normal = len(self.normals)

            texture = 0
            print(triangle.material.effect.diffuse)
            length = len(triangle.material.effect.params)
            if length != 0:
                num = num + 1

            '''
            if len(triangle.material.effect.params) != 0:
                surface, sampler = triangle.material.effect.params
                image_file = surface.image.path
                print('image_file: ', image_file)
            '''

            '''
            print(triangle.texcoords)
            if triangle.texcoords:
                surface, sampler = triangle.material.params
                image_file = surface.image.path
                print('image_file: ', image_file)
            else:
                print('none')
            '''

            '''
            if triangle.texcoords:
                coords = triangle.texcoords[0]
                surface, sampler = triangle.material.params
                image_file = surface.image.path
                print('image_file: ', image_file)


                # Only add the texture file if necessary
                if image_file not in self.textures:
                    texture = len(self.textures)
                    self.textures.append(image_file)
                else:
                    texture = self.textures.index(image_file)

            else:
                print("Warning: triangle %d has no texture" % i, file=sys.stderr)
                coords = ((0.0, 0.0), (0.0, 0.0), (0.0, 0.0))

            triangle_info = (
                vertex_ind[0], vertex_ind[1], vertex_ind[2],
                normal,
                texture,
                coords[0][0], coords[0][1],
                coords[1][0], coords[1][1],
                coords[2][0], coords[2][1],
            )

            self.triangles.append(triangle_info)
            self._vertices = concatenate((self._vertices, triangle.vertices))
            self.normals.append(tuple(triangle.normals[0]))
            '''
        print('num:', num)
    @property
    def vertices(self):
        """ Turns the vertices ndarray into a generator of tuples. """
        for vertex in self._vertices:
            yield tuple(vertex)


    def get_triangles(self):
        """
        A generator that pulls all the triangles out of the Collada scene.
        """
        for geometry in self.scene.scene.objects('geometry'):
            for primitive in geometry.primitives():
                if isinstance(primitive, collada.triangleset.BoundTriangleSet):
                    for triangle in primitive.triangles():
                        yield triangle
                else:
                    for line in primitive.lines():
                        yield line

    def scale(self, factor):
        """ Scales the vertices by the given factor """
        self._vertices = self._vertices * factor


    def permute(self, indices):
        """ Permutes the set of vertices with the given indices """
        t = self._vertices.transpose()
        t2 = t.copy()
        t2[indices[0]], t2[indices[1]], t2[indices[2]] = t
        self._vertices = t2.transpose()


    def write_model(self, outfile):
        """
        Writes a model specification to the given file-like object.
        """
        # Shorthand function for printing a formatted collection to outfile
        line = lambda template, collection: print(
            *(template % item for item in collection), sep='\n', file=outfile
        )

        line('b %s', [self.name])
        line('i %s', self.textures)
        line('v %f %f %f', self.vertices)
        line('n %f %f %f', self.normals)
        line('t %d %d %d %d %d %f %f %f %f %f %f', self.triangles)


    def print_info(self):
        print("Building Name: %s" % self.name, file=sys.stderr)
        print("Textures: %d" % len(self.textures), file=sys.stderr)
        print("Vertices: %d" % len(self._vertices), file=sys.stderr)
        print("Normals: %d" % len(self.normals), file=sys.stderr)
        print("Triangles: %d" % len(self.triangles), file=sys.stderr)


def main(argv):
    parser = argparse.ArgumentParser()

    parser.add_argument('input_file')

    parser.add_argument('output_file', nargs='?', type=argparse.FileType('w'),
                        default=sys.stdout)

    parser.add_argument('-i', '--ignore', dest='ignore', action='store_true', 
            help='Ignore errors when parsing COLLADA file')

    parser.add_argument('-v', '--verbose', action='store_true', 
            help='Print out extra info about model')

    parser.add_argument('-s', '--scale', type=float, default=None,
            help='Scale the vertices away from the origin by this factor')

    args = parser.parse_args()

    cs = ColladaToModel(args.input_file, ignore=args.ignore)

    if args.scale:
        cs.scale(args.scale)

    # Swap Y and Z axes since they apparently mean different things
    cs.permute([0, 2, 1])

    if args.verbose:
        cs.print_info()

    cs.write_model(args.output_file)


if __name__ == '__main__':
    main(sys.argv)
