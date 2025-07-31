import {createFileRoute, useSearch} from '@tanstack/react-router'
import { usePreviewPage} from "../generated/client";
import RenderJSON from "../utils/render-json.tsx";


const Preview = () => {
    // eslint-disable-next-line @typescript-eslint/ban-ts-comment
    // @ts-expect-error
    const { token, content_type } = useSearch({
        strict: false,
    })

    const page = usePreviewPage({token:token, content_type: content_type })

    return <RenderJSON data={page.data}></RenderJSON>
}

export const Route = createFileRoute('/preview')({
  component: Preview,
})

