// src/routes/$...catchall.tsx
import { createFileRoute, useLocation } from '@tanstack/react-router'
import { useFindPage } from "../generated/client";
import RenderJSON from "../utils/render-json.tsx";

export const Route = createFileRoute('/$/catchall')({
  component: CatchAllPage,
})

function CatchAllPage() {
  const location = useLocation()
  const { data, isLoading, error } = useFindPage({ html_path: location.pathname })

  if (isLoading) return <p>Loading...</p>
  if (error) return <p>Error</p>
  if (error || !data) return <p>404 - Page Not Found</p>

  return( <RenderJSON data={data}></RenderJSON>)

}
