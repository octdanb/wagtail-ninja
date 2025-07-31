import { createFileRoute } from '@tanstack/react-router'
import { useLocation } from '@tanstack/react-router'
import {useGetPageById} from "../generated/client";
import RenderJSON from "../utils/render-json.tsx";



const RouteComponent = () => {
  const location = useLocation()
  console.log(location.pathname)
  const page = useGetPageById(4)

  return <RenderJSON data={page.data}></RenderJSON>
}


export const Route = createFileRoute('/')({
  component: RouteComponent,
})