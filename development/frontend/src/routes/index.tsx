import { createFileRoute } from '@tanstack/react-router'
import { useLocation } from '@tanstack/react-router'
import {useGetPageById, useGetPageByPath} from "../generated/client";
import RenderJSON from "../utils/render-json.tsx";



const RouteComponent = () => {
  const location = useLocation()
  console.log(location.pathname)
  const page = useGetPageById(4)
  // const page =  useGetPageByPath({html_path: "/"})

  return <RenderJSON data={page.data}></RenderJSON>
}


export const Route = createFileRoute('/')({
  component: RouteComponent,
})