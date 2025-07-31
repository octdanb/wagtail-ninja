import {defineConfig} from '@kubb/core'
import {pluginReactQuery} from '@kubb/plugin-react-query'
import {pluginTs} from '@kubb/plugin-ts'
import {pluginOas} from '@kubb/plugin-oas'

export default defineConfig([
    {
        root: '.',
        input: {
            path: 'http://wagtail-ninja-django:8000/api/wagtail/v3/openapi.json',
        },
        output: {
            path: './src/generated/client',
            clean: true,
        },
        // hooks: {
        //     done: ['npx prettier --write ./src/generated/client'],
        // },
        plugins: [
            pluginOas({}),
            pluginTs({}),
            pluginReactQuery({
                suspense: false,
                output: {
                    path: './hooks',
                },
                group: {
                    type: 'tag',
                    // output: './hooks/{{tag}}Hooks',
                    name: ({ group }) => `${ group }Hooks`,
                },
                mutation: {
                    methods: ['get', 'post', 'put', 'delete'],
                },
                infinite: {
                    queryParam: 'page',
                },
                exclude: [
                ],
            }),
        ],
    },
])
