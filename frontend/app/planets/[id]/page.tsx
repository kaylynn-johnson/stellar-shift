//'use client';



type Planet = {
  pl_name: string;
  hostname: string;
  pl_rade: number | null;
  pl_orbper: number | null;
  in_hz: number | null;
};

export default async function PlanetId({
  params,
}: {
  params: Promise < {
    id: string
  } > ;
}) {
    //const params = useParams();
    const key = await params;
    //console.log(params);
    const data = await fetch(`${process.env.NEXT_PUBLIC_FASTAPI_URL}/api/planets/${key.id}`);
    const planet = await data.json();
    console.log(planet[0]);
    return (
        <ul>
            <li>Planet Name: {planet[0].pl_name}</li>
            <li>Hostname: {planet[0].hostname}</li>
            <li>Planet Radius: {planet[0].pl_rade ?? 'Unknown'}</li>
            <li>Planet Orbital Period: {planet[0].pl_orbper ?? 'Unknown'}</li>
            <li>In Habitable Zone? {planet[0].in_hz ? 'Yes' : 'No'}</li>
        </ul>
    )
}