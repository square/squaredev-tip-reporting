import { Avatar, Table, Group, Text, ScrollArea, Button } from '@mantine/core';
export interface UsersStackProps {
  id: string;
  given_name: string;
  family_name: string;
  tips: number;
  hours_worked: number;
  shifts: {
    id: string;
    location_id: string;
    timezone: string;
    start_at: string;
    end_at: string;
    wage: {
      title: string;
      hourly_rate: {
        amount: number;
        currency: string;
      };
      job_id: string;
    };
    status: string;
    version: number;
    created_at: string;
    updated_at: string;
    team_member_id: string;
    orders?: string[];
  }[];
};

const getDetailView = async({shifts, open, setSelectedDetails, setIsLoading, name}: any) => {
  setIsLoading(true)
  open()
  setSelectedDetails({
    selected_team_member_name: name,
    orders: []
  })
  // NOTE: our happy path here only expects one shift worked in a given time window
  const queryParam = shifts[0]?.orders.map((order: string) => {
      return `order_id=${order}`
    })

  const url = `/team-member-details?${queryParam.join('&')}`

  const orders = await fetch(url, {
    method: 'GET',
  }).then((response) => response.json());

  setSelectedDetails({
    selected_team_member_name: name,
    orders
  })
  setIsLoading(false)
}

export function UsersStack({ data, open, setSelectedDetails, setIsLoading }: {data: UsersStackProps[], open:any, setSelectedDetails: any, setIsLoading: any}) {
  const rows = data.map((item) => (
    <tr key={item.id}>
      <td>
        <Group spacing="sm">
          <Avatar size={40} radius={40} color="green">
            {item.given_name[0].toLocaleUpperCase()}{item.family_name[0].toLocaleUpperCase()}
          </Avatar>
          <div>
            <Text fz="sm" fw={500}>
              {item.given_name} {item.family_name}
            </Text>
            <Text c="dimmed" fz="xs">
              {Array.from(item.shifts.reduce((acc: Set<string>, shift: any) => {
                acc.add(shift.wage.title);
                return acc;
              }, new Set())).join(', ')}
            </Text>
          </div>
        </Group>
      </td>
      <td>
        <Text fz="sm">{
          (item.tips / 100).toLocaleString('en-US', {
            style: 'currency',
            currency: 'USD',
          })}
        </Text>
        <Text fz="xs" c="dimmed">
          Total Tips
        </Text>
      </td>
      <td>
        <Text fz="sm" fw={500}>
          {item.hours_worked}
        </Text>
        <Text fz="xs" c="dimmed">
          Hours Worked
        </Text>
      </td>
        {
          item?.shifts[0]?.orders ?
          (
            <>
            <td>
            <Text fz="sm" fw={500}>
              {item.shifts[0].orders.length}
            </Text>
            <Text fz="xs" c="dimmed">
              Completed Orders
            </Text>
          </td>
          <td>
          <Group spacing={0} position="right">
          <Button variant="filled" color="green" onClick={() => getDetailView({
            name: `${item.given_name} ${item.family_name}`,
            shifts: item.shifts, 
            open, 
            setSelectedDetails, 
            setIsLoading,
            })}>Details</Button>
          </Group>
          </td>
          </>)
          : ( 
            <>
            <td>
            <Text fz="sm" fw={500}>
              N/A
            </Text>
            <Text fz="xs" c="dimmed">
              Completed Orders
            </Text>
          </td>
          <td>
            <Group spacing={0} position="right">
            <Button variant="filled" color="blue" disabled={true}>Details</Button>
            </Group>
            </td>
            </>)
        }
    </tr>
  ));

  return (
    <ScrollArea>
      <Table sx={{ minWidth: 800 }} verticalSpacing="md">
        <tbody>{rows}</tbody>
      </Table>
    </ScrollArea>
  );
}
