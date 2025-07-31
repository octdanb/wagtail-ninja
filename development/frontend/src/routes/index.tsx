import { createFileRoute } from '@tanstack/react-router'
import { useLocation } from '@tanstack/react-router'
import { useFindPage } from "../generated/client";
import RenderJSON from "../utils/render-json.tsx";



const RenderPage = () => {
  const location = useLocation()
  const page = useFindPage({html_path:location.pathname})

  return <RenderJSON data={page.data}></RenderJSON>
}


export const Route = createFileRoute('/')({
  component: RenderPage,
})